"""Offline invariants for input preservation, profiles and Office package checks."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('laplace_office', Path(__file__).with_name('office.py'))
office = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(office)


def package(path, extras=None):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        for name, value in (extras or {}).items():
            archive.writestr(name, value)


class OfficeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = self.root / 'input'
        self.inputs.mkdir()
        self.output = self.root / 'output'
        self.profile = self.root / 'profile.json'
        cfg = office.read_json(office.SKILL / 'assets/company-profile.json')
        cfg['logo'] = str(office.SKILL / 'assets/company-logo.png')
        for kind, (name, _) in office.TEMPLATES.items():
            cfg[kind]['template'] = name
            package(self.root / name)
        office.write_json(self.profile, cfg)

    def test_png_preserves_original_aspect(self):
        cfg, width, height = office.load_profile(self.profile)
        self.assertEqual((width, height), (75, 67))
        self.assertEqual(office.digest(cfg['logo']), 'a7d14cbb03c0837fcb297c0eed9c1d1d012acda659464744ab62bc33e17e86c0')

    def test_directory_structure_and_output_exclusion(self):
        nested = self.inputs / 'nested'
        nested.mkdir()
        package(nested / 'sample.docx')
        package(self.inputs / 'sheet.xlsx')
        nested_output = self.inputs / 'result'
        nested_output.mkdir()
        package(nested_output / 'old.pptx')
        jobs = office.collect_inputs([self.inputs], nested_output, True)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0][1].relative_to(nested_output).as_posix(), 'nested/sample.docx')

    def test_overwrite_source_or_existing_output_is_rejected(self):
        source = self.inputs / 'sample.docx'
        package(source)
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            office.collect_inputs([source], self.inputs)
        self.output.mkdir()
        package(self.output / source.name)
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            office.collect_inputs([source], self.output)

    def test_colliding_input_names_are_rejected(self):
        package(self.inputs / 'sample.docx')
        other = self.root / 'other'
        other.mkdir()
        package(other / 'sample.docx')
        with self.assertRaisesRegex(ValueError, 'Colliding'):
            office.collect_inputs([self.inputs / 'sample.docx', other / 'sample.docx'], self.output)

    def test_legacy_file_and_signed_or_macro_package_are_rejected(self):
        legacy = self.inputs / 'old.doc'
        legacy.write_bytes(b'old')
        with self.assertRaisesRegex(ValueError, 'Unsupported file'):
            office.collect_inputs([legacy], self.output)
        for part in ('word/vbaProject.bin', '_xmlsignatures/sig1.xml'):
            path = self.inputs / 'signed.docx'
            package(path, {part: '<signature/>' if part.endswith('.xml') else b'macro'})
            with self.subTest(part=part), self.assertRaisesRegex(ValueError, 'signed'):
                office.validate_package(path)

    def test_malformed_xml_is_detected(self):
        path = self.inputs / 'bad.docx'
        package(path, {'word/document.xml': '<unclosed>'})
        with self.assertRaises(office.ET.ParseError):
            office.validate_package(path)

    def test_word_logo_is_required_in_default_and_first_headers(self):
        path = self.inputs / 'headers.docx'
        parts = {
            'word/document.xml': '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body><w:sectPr><w:headerReference w:type="default" r:id="r1"/><w:headerReference w:type="first" r:id="r2"/><w:titlePg/></w:sectPr></w:body></w:document>',
            'word/_rels/document.xml.rels': '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Target="header1.xml"/><Relationship Id="r2" Target="header2.xml"/></Relationships>',
            'word/header1.xml': '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:docPr descr="LaplaceDocs.CompanyLogo"/></w:hdr>',
            'word/header2.xml': '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'}
        package(path, parts)
        with self.assertRaisesRegex(ValueError, 'first header'):
            office.validate_word_logo(path)
        parts['word/header2.xml'] = parts['word/header1.xml']
        package(path, parts)
        office.validate_word_logo(path)
        parts['word/header1.xml'] = parts['word/header1.xml'].replace('</w:hdr>', '<wp:docPr descr="LaplaceDocs.CompanyLogo"/></w:hdr>')
        package(path, parts)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            office.validate_word_logo(path)

    def test_profile_does_not_accept_wrong_format_template(self):
        cfg = office.read_json(self.profile)
        cfg['word']['template'] = cfg['excel']['template']
        office.write_json(self.profile, cfg)
        with self.assertRaisesRegex(ValueError, 'Unsupported template'):
            office.load_profile(self.profile)

    def test_existing_templates_are_kept_without_opening_office(self):
        before = {path.name: path.read_bytes() for path in self.root.iterdir() if path.suffix in {'.dotx','.xltx','.potx'}}
        with patch.object(office, 'worker', side_effect=AssertionError('Office launched')):
            results = office.create_templates(self.profile)
        self.assertEqual(len(results), 3)
        self.assertTrue(all(item['status'] == 'existing_template_kept' for item in results))
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in before})

    def test_dry_run_creates_no_output_and_does_not_launch_office(self):
        source = self.inputs / 'sample.docx'
        package(source)
        with patch.object(office, 'worker', side_effect=AssertionError('Office launched')):
            report = office.apply([source], self.output, self.profile, dry_run=True)
        self.assertEqual(report['files'][0]['status'], 'planned')
        self.assertFalse(self.output.exists())

    def test_batch_reports_legacy_documents_instead_of_silently_omitting_them(self):
        package(self.inputs / 'sample.docx')
        (self.inputs / 'legacy.xls').write_bytes(b'legacy')
        report = office.apply([self.inputs], self.output, self.profile, dry_run=True)
        self.assertEqual({item['status'] for item in report['files']}, {'planned','unsupported_conversion_required'})

    def test_failed_content_check_keeps_source_and_withholds_output(self):
        source = self.inputs / 'sample.docx'
        package(source)
        original = source.read_bytes()
        with patch.object(office, 'worker', return_value={'success': True, 'content_unchanged': False, 'notes': []}):
            report = office.apply([source], self.output, self.profile)
        self.assertEqual(source.read_bytes(), original)
        self.assertFalse((self.output / source.name).exists())
        self.assertEqual(report['files'][0]['status'], 'failed')

    def test_embedded_object_change_withholds_output(self):
        source = self.inputs / 'sample.docx'
        package(source, {'word/embeddings/object1.bin': b'original'})
        def changed_worker(profile, path, *args, **kwargs):
            package(path, {'word/embeddings/object1.bin': b'changed'})
            return {'success': True, 'content_unchanged': True, 'notes': []}
        with patch.object(office, 'worker', side_effect=changed_worker):
            report = office.apply([source], self.output, self.profile)
        self.assertFalse((self.output / source.name).exists())
        self.assertIn('Embedded objects', report['files'][0]['error'])
        self.assertFalse(report['files'][0]['success'])

    def test_same_stem_in_different_formats_has_distinct_pdf_names(self):
        package(self.inputs / 'report.xlsx')
        package(self.inputs / 'report.pptx')
        def copy_worker(profile, path, *args, pdf=None, **kwargs):
            if pdf:
                pdf.write_bytes(b'%PDF-test-preview')
            return {'success': True, 'content_unchanged': True, 'notes': []}
        with patch.object(office, 'worker', side_effect=copy_worker):
            report = office.apply([self.inputs], self.output, self.profile, pdf=True)
        self.assertTrue(all(item['status'] == 'processed_needs_visual_review' for item in report['files']))
        self.assertEqual({Path(item['preview_pdf']).name for item in report['files']},
                         {'report.xlsx.review.pdf','report.pptx.review.pdf'})

    def test_existing_pdf_is_rejected_before_opening_office(self):
        package(self.inputs / 'report.xlsx')
        self.output.mkdir()
        (self.output / 'report.xlsx.review.pdf').write_bytes(b'keep')
        with patch.object(office, 'worker', side_effect=AssertionError('Office launched')):
            with self.assertRaisesRegex(ValueError, 'PDF preview would overwrite'):
                office.apply([self.inputs], self.output, self.profile, pdf=True)


if __name__ == '__main__':
    unittest.main()
