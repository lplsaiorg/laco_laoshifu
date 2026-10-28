"""Observable invariants of local provenance and retrieval; no external services."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'kb.py'
spec = importlib.util.spec_from_file_location('kd_kb', SCRIPT)
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'source'
        self.upstream = self.base / 'upstream'
        self.upstream.mkdir()
        self.root.mkdir()
        (self.root / 'README.md').write_text('# 测试知识库\n', encoding='utf-8')
        (self.upstream / '01.md').write_bytes(
            '# 管式设备\r\n\r\n## 氮化硅\r\nPECVD沉积氮化硅 SiNₓ:H。\r\n'.encode('utf-8'))
        kb.write_json(self.root / 'glossary.json', {
            'terms': [{'term': 'SiNx', 'aliases': ['氮化硅', 'SiNₓ:H'],
                       'sources': ['references/kd/01.md']}]})
        self.quiet(kb.snapshot, self.root, self.upstream)
        self.quiet(kb.index, self.root)

    def quiet(self, fn, *args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return fn(*args, **kwargs)

    def test_snapshot_preserves_exact_bytes_and_manifest(self):
        copy = self.root / 'references/kd/01.md'
        self.assertEqual(copy.read_bytes(), (self.upstream / '01.md').read_bytes())
        self.quiet(kb.verify, self.root)

    def test_reindex_cannot_hide_snapshot_tampering(self):
        copy = self.root / 'references/kd/01.md'
        copy.write_text('# 修改后的原文\n', encoding='utf-8')
        self.quiet(kb.index, self.root)
        with self.assertRaisesRegex(ValueError, '原文快照与来源清单不一致'):
            self.quiet(kb.verify, self.root)

    def test_update_requires_explicit_option_and_keeps_deleted_history(self):
        (self.upstream / '01.md').write_text('# 新版本\n', encoding='utf-8')
        before = (self.root / 'references/kd/01.md').read_bytes()
        with self.assertRaisesRegex(ValueError, '--update'):
            self.quiet(kb.snapshot, self.root, self.upstream)
        self.assertEqual(before, (self.root / 'references/kd/01.md').read_bytes())
        self.quiet(kb.snapshot, self.root, self.upstream, True)
        (self.upstream / '01.md').unlink()
        (self.upstream / '02.md').write_text('# 新文档\n', encoding='utf-8')
        self.quiet(kb.snapshot, self.root, self.upstream)
        self.assertTrue((self.root / 'references/kd/01.md').exists())
        records = kb.read_json(self.root / 'manifest.json')['files']
        self.assertEqual(records[0]['source_status'], 'not_in_latest_import')

    def test_alias_search_finds_original_and_real_lines(self):
        hit = kb.search(self.root, 'SiNx', 'references', 1)[0]
        self.assertEqual(hit['path'], 'references/kd/01.md')
        self.assertIn('氮化硅', hit['excerpt'])
        text = (self.root / hit['path']).read_text(encoding='utf-8').splitlines()
        self.assertIn('氮化硅', '\n'.join(text[hit['line_start'] - 1:hit['line_end']]))

    def test_search_and_index_detect_stale_new_and_changed_documents(self):
        new = self.root / 'knowledge' / 'states.md'
        new.parent.mkdir()
        new.write_text('# 状态\nOEE状态需要确认。\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '索引已过期'):
            kb.search(self.root, 'OEE')
        with self.assertRaisesRegex(ValueError, '索引已过期'):
            self.quiet(kb.index, self.root, True)
        self.quiet(kb.index, self.root)
        new.write_text('# 状态\n改动\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '索引已过期'):
            kb.search(self.root, 'OEE')

    def test_history_status_is_visible_in_retrieval(self):
        (self.upstream / '01.md').unlink()
        (self.upstream / '02.md').write_text('# 新文档\nNEWENTRY\n', encoding='utf-8')
        self.quiet(kb.snapshot, self.root, self.upstream)
        self.quiet(kb.index, self.root)
        hit = kb.search(self.root, '氮化硅', 'references', 1)[0]
        self.assertEqual(hit['source_status'], 'not_in_latest_import')

    def test_cli_runs_from_unrelated_working_directory(self):
        done = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
                               'search', '氮化硅', '--category', 'references', '--json'],
                              cwd=self.base, capture_output=True, encoding='utf-8')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['results'][0]['path'], 'references/kd/01.md')

    def test_local_missing_links_are_reported_without_requesting_urls(self):
        path = self.root / 'knowledge.md'
        path.write_text('[不存在](missing.md)\n[远程](https://example.invalid/)\n', encoding='utf-8')
        errors = kb.link_errors(path)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing.md', errors[0])

    def test_unsafe_manifest_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '超出知识库'):
            kb.inside(self.root, '../../outside.md')

    def test_empty_query_and_invalid_limit_are_rejected(self):
        with self.assertRaises(ValueError):
            kb.search(self.root, ' ')
        with self.assertRaises(ValueError):
            kb.search(self.root, 'SiNx', limit=0)

    def abbreviation_fixture(self):
        terms = kb.read_json(self.root / 'glossary.json')['terms']
        terms.extend([
            {'term': 'PECVD', 'abbreviation': 'PECVD', 'aliases': ['等离子增强沉积'],
             'english_full_name': 'Plasma-Enhanced Chemical Vapor Deposition',
             'chinese_full_name': '等离子体增强化学气相沉积', 'category': 'process',
             'usage': '区分沉积工序', 'notes': '先确认工序',
             'short_names': [{'name': '等离子增强沉积', 'kind': 'chinese_short', 'status': 'curated',
                              'scope': '测试中明确维护的同概念名称', 'sources': ['references/kd/01.md']}],
             'full_name_status': 'curated_translation', 'status': 'reference_summary',
             'meaning': '等离子增强沉积', 'sources': ['references/kd/01.md']},
            {'term': 'HJT', 'abbreviation': 'HJT', 'aliases': ['HIT', 'SHJ'],
             'english_full_name': 'Heterojunction Technology', 'chinese_full_name': '异质结技术',
             'category': 'technology', 'usage': '识别技术路线', 'notes': '',
             'full_name_status': 'curated_translation', 'status': 'reference_summary',
             'meaning': '异质结路线', 'sources': ['references/kd/01.md']},
            {'term': 'HIT', 'abbreviation': 'HIT', 'aliases': [],
             'english_full_name': 'Heterojunction with Intrinsic Thin-Layer',
             'chinese_full_name': '本征薄层异质结', 'category': 'technology',
             'usage': '区分名称', 'notes': '不能用HJT全称直接替代',
             'full_name_status': 'source_explicit', 'status': 'reference_summary',
             'meaning': '名称展开', 'sources': ['references/kd/01.md']},
        ])
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        return terms

    def test_abbreviation_lookup_normalizes_case_unicode_and_queries_full_names(self):
        self.abbreviation_fixture()
        for query in ('pecvd', 'ＰＥＣＶＤ', '等离子体增强化学气相沉积',
                      'plasma enhanced chemical vapor deposition', '等离子增强沉积'):
            with self.subTest(query=query):
                hit = kb.abbreviations(self.root, query)[0]
                self.assertEqual(hit['abbreviation'], 'PECVD')
                self.assertTrue(hit['sources'])
                self.assertEqual(hit['full_name_status'], 'curated_translation')

    def test_abbreviation_list_filters_out_regular_terms_and_applies_category_limit(self):
        self.abbreviation_fixture()
        self.assertEqual(len(kb.abbreviations(self.root)), 3)
        technology = kb.abbreviations(self.root, category='technology')
        self.assertEqual({hit['abbreviation'] for hit in technology}, {'HJT', 'HIT'})
        self.assertEqual(len(kb.abbreviations(self.root, limit=1)), 1)
        self.assertEqual(kb.abbreviations(self.root, 'unlisted-acronym'), [])

    def test_exact_abbreviation_wins_over_shared_alias(self):
        self.abbreviation_fixture()
        hits = kb.abbreviations(self.root, 'hit')
        self.assertEqual([hit['abbreviation'] for hit in hits], ['HIT'])
        self.assertIn('Intrinsic', hits[0]['english_full_name'])

    def test_same_abbreviation_with_distinct_contexts_returns_all_meanings(self):
        terms = self.abbreviation_fixture()
        alternative = dict(terms[-1], term='HIT-other-context', category='testing',
                           usage='测试上下文示例')
        terms.append(alternative)
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        self.assertEqual(len(kb.abbreviations(self.root, 'HIT')), 2)
        self.assertEqual(len(kb.abbreviations(self.root, 'HIT', 'testing')), 1)

    def test_abbreviation_cli_does_not_need_document_catalog_or_current_directory(self):
        self.abbreviation_fixture()
        # This lookup remains usable while the search catalog is stale or unavailable.
        (self.root / 'catalog.json').unlink()
        done = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
                               'abbr', 'ＰＥＣＶＤ', '--json'],
                              cwd=self.base, capture_output=True, encoding='utf-8')
        self.assertEqual(done.returncode, 0, done.stderr)
        output = json.loads(done.stdout)
        self.assertEqual(output['count'], 1)
        self.assertEqual(output['results'][0]['abbreviation'], 'PECVD')

    def test_full_name_metadata_expands_original_document_search(self):
        self.abbreviation_fixture()
        self.quiet(kb.index, self.root)
        hits = kb.search(self.root, 'plasma enhanced chemical vapor deposition', 'references')
        self.assertTrue(hits)
        self.assertIn('PECVD', hits[0]['excerpt'])

    def test_abbreviation_metadata_and_options_reject_incomplete_values(self):
        terms = self.abbreviation_fixture()
        terms[-1]['english_full_name'] = ''
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        with self.assertRaisesRegex(ValueError, 'english_full_name'):
            kb.abbreviations(self.root, 'HIT')
        self.quiet(kb.index, self.root)
        with self.assertRaisesRegex(ValueError, 'english_full_name'):
            self.quiet(kb.verify, self.root)
        for options in ({'limit': 0}, {'limit': 201}, {'category': 'unknown'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                kb.abbreviations(self.root, **options)

    def concept_fixture(self):
        terms = self.abbreviation_fixture()
        def short(name, kind='dataset_code', status='user_confirmed', auto_expand=True):
            return {'name': name, 'kind': kind, 'status': status, 'scope': '本测试约定的工作语境',
                    'sources': ['references/kd/01.md'], 'auto_expand': auto_expand}
        next(term for term in terms if term['term'] == 'PECVD')['short_names'] = [short('PE', 'english_short')]
        terms.extend([
            {'term': '硼扩散', 'aliases': ['硼扩', 'BK'], 'category': 'process',
             'meaning': '硼扩散工序', 'sources': ['references/kd/01.md'],
             'short_names': [short('硼扩', 'chinese_short'), short('BK')]},
            {'term': '磷扩散', 'aliases': ['PK'], 'category': 'process',
             'meaning': '磷扩散工序', 'sources': ['references/kd/01.md'],
             'short_names': [short('PK')]},
            {'term': '退火（旧标签）', 'aliases': ['pk', 'TX'], 'category': 'process',
             'meaning': '原文标签待核实', 'sources': ['references/kd/01.md'],
             'short_names': [short('pk', status='dataset_explicit', auto_expand=False),
                             short('TX', status='dataset_inferred', auto_expand=False)]},
        ])
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        return terms, short

    def test_concept_can_have_chinese_and_multiple_letter_short_names_without_english_acronym(self):
        self.concept_fixture()
        for query in ('硼扩散', '硼扩', 'BK', 'ｂｋ'):
            with self.subTest(query=query):
                hits = kb.abbreviations(self.root, query)
                self.assertEqual([hit['term'] for hit in hits], ['硼扩散'])
                self.assertEqual({record['name'] for record in hits[0]['short_names']}, {'硼扩', 'BK'})
                self.assertNotIn('english_full_name', hits[0])
        self.assertEqual(kb.abbreviations(self.root, 'PE')[0]['term'], 'PECVD')

    def test_user_mapping_is_ranked_first_and_conflicting_candidate_does_not_expand(self):
        self.concept_fixture()
        hits = kb.abbreviations(self.root, 'PK')
        self.assertEqual([hit['term'] for hit in hits], ['磷扩散', '退火（旧标签）'])
        self.assertEqual(kb.abbreviations(self.root, 'TX')[0]['term'], '退火（旧标签）')
        # The user mapping is scoped. A competing historical meaning means an
        # unqualified PK query must remain lexical until context is reviewed.
        self.assertNotIn('磷扩散', kb.query_terms(self.root, 'PK')[1])
        for query in ('PK', 'TX'):
            self.assertNotIn('退火（旧标签）', kb.query_terms(self.root, query)[1])

    def test_multiple_physical_meanings_of_same_name_are_visible_but_not_auto_merged(self):
        terms, short = self.concept_fixture()
        for name in ('方阻检测数据', '膜厚检测数据'):
            terms.append({'term': name, 'category': 'testing', 'aliases': [],
                          'sources': ['references/kd/01.md'], 'meaning': name,
                          'short_names': [short('OD', status='dataset_explicit')]})
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        self.assertEqual(len(kb.abbreviations(self.root, 'OD')), 2)
        # Even two explicit mappings cannot become one global identity.
        self.assertEqual(kb.query_terms(self.root, 'OD')[1], [])

    def test_confirmed_short_name_expands_search_to_original_full_concept(self):
        self.concept_fixture()
        (self.upstream / '01.md').write_text('# 工艺\n\n## 硼扩散\n硼扩散工序的参考说明。\n', encoding='utf-8')
        self.quiet(kb.snapshot, self.root, self.upstream, True)
        self.quiet(kb.index, self.root)
        hits = kb.search(self.root, 'BK', 'references')
        self.assertTrue(hits)
        self.assertIn('硼扩散', hits[0]['excerpt'])

    def test_generated_crosswalk_remains_in_sync_after_concept_change(self):
        terms, _ = self.concept_fixture()
        workflow = self.root / 'workflows/name-disambiguation.md'
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text('# 名称消歧\n先看上下文，仍无法判断时向用户确认。\n', encoding='utf-8')
        self.quiet(kb.crosswalk, self.root)
        self.quiet(kb.crosswalk, self.root, True)
        content = (self.root / 'knowledge/name-crosswalk.md').read_text(encoding='utf-8')
        self.assertIn('硼扩散', content)
        self.assertIn('BK', content)
        self.quiet(kb.index, self.root)
        self.quiet(kb.verify, self.root)
        terms[-1]['notes'] = '新核实的适用范围'
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        self.quiet(kb.index, self.root)
        with self.assertRaisesRegex(ValueError, '对照表已过期'):
            self.quiet(kb.verify, self.root)
        self.quiet(kb.crosswalk, self.root)
        self.quiet(kb.index, self.root)
        self.quiet(kb.verify, self.root)

    def test_missing_category_and_missing_short_name_evidence_are_reported(self):
        terms, _ = self.concept_fixture()
        del terms[-1]['category']
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        with self.assertRaisesRegex(ValueError, '分类无效'):
            self.quiet(kb.crosswalk, self.root)
        terms[-1]['category'] = 'process'
        terms[-1]['short_names'][0]['sources'] = ['evidence/missing.json']
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        self.quiet(kb.index, self.root)
        with self.assertRaisesRegex(ValueError, '简称出处缺失'):
            self.quiet(kb.verify, self.root)

    def test_related_search_hints_are_not_treated_as_same_concept_names(self):
        terms, _ = self.concept_fixture()
        boron = next(term for term in terms if term['term'] == '硼扩散')
        boron['aliases'].append('BCl3')
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        self.assertEqual(kb.abbreviations(self.root, 'BCl3'), [])
        # Search can still use this related hint to locate relevant background.
        self.assertIn('硼扩散', kb.query_terms(self.root, 'BCl3')[1])

    def test_disambiguation_reports_conflict_even_when_alternative_cannot_auto_expand(self):
        self.concept_fixture()
        report = kb.name_disambiguation(self.root, 'PK')
        self.assertEqual(report['status'], 'ambiguous')
        self.assertTrue(report['requires_context_review'])
        self.assertEqual({item['term'] for item in report['candidates']}, {'磷扩散', '退火（旧标签）'})
        self.assertTrue(all(item['scopes'] and item['sources'] for item in report['candidates']))
        self.assertIn('PK', report['confirmation_prompt'])

    def test_disambiguation_distinguishes_listing_single_partial_and_unknown_names(self):
        self.concept_fixture()
        self.assertFalse(kb.name_disambiguation(self.root)['requires_context_review'])
        self.assertEqual(kb.name_disambiguation(self.root)['status'], 'not_applicable')
        one = kb.name_disambiguation(self.root, 'BK')
        self.assertEqual(one['status'], 'single_candidate')
        self.assertTrue(one['requires_context_review'])
        self.assertNotIn('confirmation_prompt', one)
        self.assertEqual(kb.name_disambiguation(self.root, '等离子')['status'], 'possible_matches')
        missing = kb.name_disambiguation(self.root, 'UNKNOWN-CODE')
        self.assertEqual(missing['status'], 'not_found')
        self.assertTrue(missing['confirmation_prompt'])

    def test_cli_filters_and_limits_do_not_hide_ambiguity(self):
        terms, short = self.concept_fixture()
        for name, category in (('方阻检测数据', 'testing'), ('膜厚检测数据', 'process')):
            terms.append({'term': name, 'category': category, 'aliases': [],
                          'sources': ['references/kd/01.md'], 'meaning': name,
                          'short_names': [short('OD', status='dataset_explicit')]})
        kb.write_json(self.root / 'glossary.json', {'terms': terms})
        done = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
                               'abbr', 'OD', '--category', 'testing', '--limit', '1', '--json'],
                              cwd=self.base, capture_output=True, encoding='utf-8')
        self.assertEqual(done.returncode, 0, done.stderr)
        output = json.loads(done.stdout)
        self.assertEqual(output['count'], 1)
        self.assertEqual(output['disambiguation']['status'], 'ambiguous')
        self.assertEqual(len(output['disambiguation']['candidates']), 2)


if __name__ == '__main__':
    unittest.main()
