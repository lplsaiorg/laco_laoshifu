#!/usr/bin/env python3
"""KD knowledge retrieval and provenance checks. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("references", "knowledge", "workflows", "templates", "evidence")
ABBREVIATION_CATEGORIES = {
    "technology": "电池技术", "equipment": "设备", "process": "工艺",
    "testing": "测试表征", "materials": "材料", "metrics": "指标",
}
NAME_KINDS = {"chinese_short": "中文简称", "english_short": "英文简称",
              "dataset_code": "数据集代码", "symbol": "指标/字段符号"}
NAME_STATUSES = {"user_confirmed": "用户确认", "dataset_explicit": "数据集明确",
                 "dataset_inferred": "候选待确认", "knowledge_explicit": "知识资料明确",
                 "curated": "整理补充"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"路径超出知识库: {relative}")
    return path


def headings(text: str):
    result = []
    fence = None
    for line_no, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker[1][0]
            elif marker[1][0] == fence:
                fence = None
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match and fence is None:
            result.append({"line": line_no, "level": len(match[1]), "title": match[2]})
    return result


def documents(root: Path):
    paths = [root / "README.md", root / "glossary.json"]
    for category in CATEGORIES:
        paths.extend((root / category).rglob("*"))
    return sorted({p for p in paths if p.is_file() and p.suffix.lower() in {".md", ".yaml", ".json"}},
                  key=lambda p: p.relative_to(root).as_posix())


def build_catalog(root: Path):
    manifest_path = root / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {"files": []}
    origins = {item["path"]: item for item in manifest["files"]}
    result = []
    for path in documents(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        sections = headings(text)
        category = rel.split("/")[0] if "/" in rel else "knowledge"
        origin = origins.get(rel)
        result.append({
            "id": rel, "path": rel, "category": category,
            "title": sections[0]["title"] if sections else path.stem,
            "sha256": sha256(path), "bytes": path.stat().st_size,
            "line_count": len(text.splitlines()), "sections": sections,
            "evidence": "source_snapshot" if origin else (
                "dataset_evidence" if category == "evidence" else "curated_guidance"),
            "source_status": origin.get("source_status", "present") if origin else None,
        })
    return {"schema_version": 1, "documents": result}


def index(root: Path, check: bool = False):
    expected = build_catalog(root)
    path = root / "catalog.json"
    if check:
        if not path.exists() or read_json(path) != expected:
            raise ValueError("目录索引已过期，请运行 index；index 不会重签原文快照。")
        print(f"索引一致: {len(expected['documents'])} 份文档")
    else:
        write_json(path, expected)
        print(f"已建立索引: {len(expected['documents'])} 份文档")


def snapshot(root: Path, source: Path, update: bool = False):
    source = source.resolve(strict=True)
    destination = root / "references" / "kd"
    destination.mkdir(parents=True, exist_ok=True)
    if source == destination.resolve():
        raise ValueError("不能以快照目录本身作为导入来源。")
    files = sorted(source.glob("*.md"))
    if not files:
        raise ValueError(f"来源没有 Markdown: {source}")
    old_path = root / "manifest.json"
    old = read_json(old_path) if old_path.exists() else {"files": []}
    previous = {item["path"]: item for item in old["files"]}
    changes = [p.name for p in files if (destination / p.name).exists()
               and sha256(p) != sha256(destination / p.name)]
    if changes and not update:
        raise ValueError("现有快照有变化，审阅后用 --update 导入: " + ", ".join(changes))
    # Validate every input before copying; no shell evaluation or network calls.
    for path in files:
        path.read_text(encoding="utf-8-sig")
    imported = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records = dict(previous)
    seen = set()
    for path in files:
        target = destination / path.name
        shutil.copy2(path, target)
        rel = target.relative_to(root).as_posix()
        seen.add(rel)
        records[rel] = {"path": rel, "source_name": path.name, "sha256": sha256(target),
                        "bytes": target.stat().st_size, "source_status": "present",
                        "imported_at_utc": imported,
                        "source_modified_at_utc": datetime.fromtimestamp(
                            path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")}
    for rel in records.keys() - seen:
        records[rel]["source_status"] = "not_in_latest_import"
    write_json(old_path, {"schema_version": 1, "source_label": "External reference collection",
                         "last_imported_at_utc": imported,
                         "files": [records[key] for key in sorted(records)]})
    print(f"已复制 {len(files)} 份原文；保留 {len(records) - len(seen)} 份历史原文。请运行 index 和 verify。")


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def contains(text: str, term: str) -> bool:
    if re.fullmatch(r"[a-z0-9_-]+", term):
        return re.search(r"(?<![a-z0-9_])" + re.escape(term) + r"(?![a-z0-9_])", text) is not None
    return term in text


def active_short_name(record: dict) -> bool:
    return record.get("status") != "dataset_inferred" and record.get("auto_expand", True)


def term_names(term: dict, for_search: bool = False):
    """Reuse the glossary for both abbreviation lookup and document expansion."""
    records = term.get("short_names", [])
    active = {normalize(record["name"]) for record in records if active_short_name(record)}
    blocked = {normalize(record["name"]) for record in records} - active if for_search else set()
    return list(dict.fromkeys(name for name in [
        term["term"], *term.get("aliases", []), term.get("abbreviation"),
        term.get("english_full_name"), term.get("chinese_full_name"),
        *(record["name"] for record in records if not for_search or active_short_name(record)),
    ] if isinstance(name, str) and name.strip() and normalize(name) not in blocked))


def lookup_names(term: dict):
    # Legacy aliases also include gas sources, layers and related search hints.
    # They remain searchable, but are not evidence of concept identity.
    return [name for name in [term["term"], term.get("abbreviation"),
            term.get("english_full_name"), term.get("chinese_full_name"),
            *(record["name"] for record in term.get("short_names", []))]
            if isinstance(name, str) and name.strip()]


def abbreviation_key(value: str) -> str:
    return re.sub(r"[\s_\-\u2010-\u2015]+", "", normalize(value))


def phrase_key(value: str) -> str:
    return re.sub(r"[\s_\-\u2010-\u2015]+", " ", normalize(value)).strip()


def abbreviation_errors(glossary: dict):
    errors = []
    for term in glossary["terms"]:
        records = term.get("short_names", [])
        if not isinstance(records, list):
            errors.append(f"简称列表无效: {term.get('term')}")
            records = []
        for record in records:
            if not isinstance(record, dict):
                errors.append(f"简称记录无效: {term.get('term')}")
                continue
            for field in ("name", "scope"):
                if not isinstance(record.get(field), str) or not record[field].strip():
                    errors.append(f"简称字段缺失或为空: {term.get('term')}: {field}")
            if record.get("kind") not in NAME_KINDS or record.get("status") not in NAME_STATUSES:
                errors.append(f"简称类型或确认状态无效: {term.get('term')}: {record.get('name')}")
            if not isinstance(record.get("sources"), list) or not record["sources"]:
                errors.append(f"简称缺少出处: {term.get('term')}: {record.get('name')}")
            if "auto_expand" in record and not isinstance(record["auto_expand"], bool):
                errors.append(f"简称auto_expand必须是布尔值: {term.get('term')}")
            if record.get("status") == "dataset_inferred" and record.get("auto_expand", False):
                errors.append(f"候选简称不能自动展开: {term.get('term')}: {record.get('name')}")
        if (term.get("abbreviation") or records) and term.get("category") not in ABBREVIATION_CATEGORIES:
            errors.append(f"简称/缩写概念分类无效: {term.get('term')}: {term.get('category')}")
        if "abbreviation" not in term:
            continue
        for field in ("abbreviation", "english_full_name", "chinese_full_name", "usage"):
            if not isinstance(term.get(field), str) or not term[field].strip():
                errors.append(f"缩写字段缺失或为空: {term.get('term')}: {field}")
        if term.get("full_name_status") not in {"source_explicit", "curated_translation"}:
            errors.append(f"缩写全称依据无效: {term.get('term')}")
        if not isinstance(term.get("notes", ""), str):
            errors.append(f"缩写注意事项必须是文本: {term.get('term')}")
        if not isinstance(term.get("sources"), list) or not term["sources"]:
            errors.append(f"缩写缺少出处: {term.get('term')}")
    return errors


def abbreviations(root: Path, query: str = "", category: str | None = None, limit: int = 200):
    """Read the single glossary directly, even if the document catalog is unavailable."""
    if not 1 <= limit <= 200:
        raise ValueError("limit 必须在 1 到 200 之间。")
    if category is not None and category not in ABBREVIATION_CATEGORIES:
        raise ValueError(f"未知缩写分类: {category}")
    glossary = read_json(root / "glossary.json")
    errors = abbreviation_errors(glossary)
    if errors:
        raise ValueError("\n".join(errors))
    terms = [dict(term) for term in glossary["terms"] if (term.get("abbreviation") or term.get("short_names"))
             and (category is None or term.get("category") == category)]
    query = phrase_key(query)
    if query:
        # Confirmed short names may share a name with another concept. Keep every
        # explicit meaning; legacy related aliases must not hide a standard name.
        exact = [term for term in terms
                 if any(abbreviation_key(name) == abbreviation_key(query)
                        for name in [term["term"], term.get("abbreviation", "")]
                        if name)
                 or any(abbreviation_key(record["name"]) == abbreviation_key(query)
                        for record in term.get("short_names", []))]
        if exact:
            terms = exact  # Return every meaning of an exact abbreviation, not just the first.
        else:
            terms = [term for term in terms
                     if any(query in phrase_key(name) for name in lookup_names(term))]
            terms.sort(key=lambda term: (
                not any(query == phrase_key(name) for name in lookup_names(term)),
                not phrase_key(term.get("abbreviation", term["term"])).startswith(query),
                normalize(term.get("abbreviation", term["term"])), term["term"]))
            return terms[:limit]
    def rank(term):
        matched = [record for record in term.get("short_names", [])
                   if query and abbreviation_key(record["name"]) == abbreviation_key(query)]
        priority = min(({"user_confirmed": 0, "dataset_inferred": 3}.get(record["status"], 1)
                        for record in matched), default=1)
        return priority, normalize(term.get("abbreviation", term["term"])), term["term"]
    return sorted(terms, key=rank)[:limit]


def name_disambiguation(root: Path, query: str = ""):
    """Report lexical candidates; semantic choice belongs to context review."""
    result = {"status": "not_applicable", "requires_context_review": False,
              "next_action": "清单浏览不代表任何名称已在当前任务中消歧。", "candidates": []}
    if not phrase_key(query):
        return result
    # Do not let display limits or category filters hide a competing meaning.
    hits = abbreviations(root, query, limit=200)
    exact = [term for term in hits if any(abbreviation_key(name) == abbreviation_key(query)
                                        for name in lookup_names(term))]
    candidates = exact or hits
    for term in candidates:
        records = [record for record in term.get("short_names", [])
                   if abbreviation_key(record["name"]) == abbreviation_key(query)]
        result["candidates"].append({
            "term": term["term"],
            "scopes": list(dict.fromkeys(record["scope"] for record in records)),
            "sources": list(dict.fromkeys([*term.get("sources", []),
                         *(ref for record in records for ref in record["sources"])])),
        })
    result["requires_context_review"] = True
    if len(exact) > 1:
        result["status"] = "ambiguous"
        result["next_action"] = "先用原句、工序设备、数据来源、字段邻列、单位与版本复核候选；仍有多种合理含义或证据冲突时，必须向用户确认。"
        choices = "；".join(f"{i}) {candidate['term']}" for i, candidate in enumerate(result["candidates"][:3], 1))
        result["confirmation_prompt"] = f"这里的 {query} 指哪一种含义：{choices}？请结合原句或数据来源确认。"
    elif len(exact) == 1:
        result["status"] = "single_candidate"
        result["next_action"] = "唯一词典候选不等于当前语境已确认。核对适用范围及上下文后使用；范围不符或证据不足时向用户确认。"
    elif hits:
        result["status"] = "possible_matches"
        result["next_action"] = "当前只是部分名称匹配。结合原句和来源缩小候选；无法明确含义时向用户确认，不选第一条代替判断。"
    else:
        result["status"] = "not_found"
        result["next_action"] = "先检索原句及数据来源；仍无法判断时向用户确认中文含义或索取原句、字段与来源，不能按拼音或词频猜测。"
        result["confirmation_prompt"] = f"请确认 {query} 在这里的中文含义，或提供它出现的原句、字段及数据来源。"
    return result


def render_crosswalk(glossary: dict) -> str:
    """Generate the readable table from the single concept and alias registry."""
    errors = abbreviation_errors(glossary)
    if errors:
        raise ValueError("\n".join(errors))
    def cell(value):
        return str(value or "—").replace("|", "\\|").replace("\n", "<br>")
    lines = ["# 常用简称与缩写对照表", "",
             "由 `tools/kb.py crosswalk` 从 [glossary.json](../glossary.json) 生成，请维护主表后重新生成。", "",
             "一行对应一个概念；中文简称、英文缩写、现场代码与指标符号可以共同指向它。",
             "确认状态与适用范围属于每个名称，局部记录不代表全厂规则。候选及禁用自动展开的名称仅供查证，不作为自动同义替换。", "",
             "用户明确确认的工作约定仅在其适用范围内优先。新数据来源的名称含义仍须核实，不能从拼音首字母或文件共现猜定。", "",
             "同一简称可能对应多个中文概念。先按工序、设备、字段、单位、路径与版本推断并给出依据；仍不能判断时向用户确认，确认前暂停依赖该含义的处理。见[名称消歧工作流](../workflows/name-disambiguation.md)。", ""]
    terms = [term for term in glossary["terms"] if term.get("abbreviation") or term.get("short_names")]
    for category, label in ABBREVIATION_CATEGORIES.items():
        group = sorted((term for term in terms if term.get("category") == category),
                       key=lambda term: normalize(term["term"]))
        if not group:
            continue
        lines.extend([f"## {label}", "", "| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |",
                      "|---|---|---|---|---|---|"])
        for term in group:
            records = term.get("short_names", [])
            names = list(dict.fromkeys(record["name"] for record in records
                                       if record["name"] != term.get("abbreviation")))
            scopes = [f"{record['name']}：{NAME_STATUSES[record['status']]}；{record['scope']}"
                      + ("；不自动展开" if not active_short_name(record) else "") for record in records]
            refs = list(dict.fromkeys([*term.get("sources", []),
                                       *(ref for record in records for ref in record["sources"])]))
            links = " / ".join(f"[来源{i}](../{ref.split('#', 1)[0]})" for i, ref in enumerate(refs, 1))
            concept = term.get("chinese_full_name") or term["term"]
            # A scoped canonical label is useful even when it has a display translation.
            if not term.get("abbreviation") and term["term"] != concept:
                concept = f"{concept}（{term['term']}）"
            full_name = term.get("english_full_name", "")
            standard = term.get("abbreviation", "")
            if full_name:
                standard += f"<br>{full_name}"
                standard += "<br>" + ("原文明示" if term.get("full_name_status") == "source_explicit" else "整理补充")
            lines.append("| " + " | ".join([
                cell(concept), cell(standard), cell("、".join(names)),
                cell("\n".join(scopes)), cell(term.get("notes", "")), links or "—"]) + " |")
        lines.append("")
    lines.extend(["## 查证方式", "", "```powershell",
                  'python source/tools/kb.py abbr "硼扩散"', 'python source/tools/kb.py abbr "BK" --json',
                  'python source/tools/kb.py abbr "PE"', 'python source/tools/kb.py abbr "PK"',
                  "```", "", "来源中的证据摘录保留数据集相对路径与行号；原始数据集保持只读，不纳入本表复制。", ""])
    return "\n".join(lines)


def crosswalk(root: Path, check: bool = False):
    expected = render_crosswalk(read_json(root / "glossary.json"))
    path = root / "knowledge" / "name-crosswalk.md"
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            raise ValueError("简称对照表已过期，请运行 crosswalk，再运行 index。")
        print("简称对照表与术语主表一致")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        print(f"已生成简称对照表: {path}")


def query_terms(root: Path, query: str):
    query = normalize(query).strip()
    primary = re.findall(r"[a-z0-9]+(?:[._-][a-z0-9]+)*|[\u3400-\u9fff]+", query)
    aliases = set()
    glossary = root / "glossary.json"
    if glossary.exists():
        terms = read_json(glossary).get("terms", [])
        owners = {}
        for term in terms:
            for record in term.get("short_names", []):
                # A disabled historical meaning is still evidence of ambiguity.
                # Without context, do not expand the same letters into one meaning.
                owners.setdefault(abbreviation_key(record["name"]), set()).add(term["term"])
        ambiguous = {name for name, concepts in owners.items() if len(concepts) > 1}
        for term in terms:
            names = [normalize(name) for name in term_names(term, for_search=True)
                     if abbreviation_key(name) not in ambiguous]
            if any(contains(query, name) or contains(phrase_key(query), phrase_key(name)) for name in names):
                aliases.update(names)
    grams = set()
    for part in primary:
        if re.fullmatch(r"[\u3400-\u9fff]{3,}", part):
            grams.update(part[i:i + 2] for i in range(len(part) - 1))
    return list(dict.fromkeys(primary)), sorted(aliases - set(primary)), sorted(grams)


def chunks(text: str):
    lines = text.splitlines()
    sections = headings(text)
    starts = sorted({0, *(section["line"] - 1 for section in sections)})
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        title = next((section["title"] for section in reversed(sections) if section["line"] <= start + 1), "")
        for offset in range(start, end, 50):
            stop = min(offset + 55, end)
            yield offset + 1, stop, title, "\n".join(lines[offset:stop])


def search(root: Path, query: str, category: str | None = None, limit: int = 5):
    if not 1 <= limit <= 50:
        raise ValueError("limit 必须在 1 到 50 之间。")
    if not normalize(query).strip():
        raise ValueError("检索词不能为空。")
    catalog_path = root / "catalog.json"
    if not catalog_path.exists():
        raise ValueError("缺少 catalog.json，请先运行 index。")
    catalog = read_json(catalog_path)
    # Include newly added files and manifest status changes in the freshness check.
    if catalog != build_catalog(root):
        raise ValueError("目录索引已过期，请运行 index 或用 rg 检索原文。")
    primary, aliases, grams = query_terms(root, query)
    result = []
    for doc in catalog["documents"]:
        if category and doc["category"] != category:
            continue
        path = inside(root, doc["path"])
        if not path.exists() or sha256(path) != doc["sha256"]:
            raise ValueError(f"目录索引已过期: {doc['path']}；请运行 index。")
        text = path.read_text(encoding="utf-8-sig")
        for start, end, title, content in chunks(text):
            body, heading = normalize(content), normalize(title)
            exact = [term for term in primary if contains(body, term)]
            expanded = [term for term in aliases if contains(body, term)]
            partial = [term for term in grams if contains(body, term)]
            score = 10 * len(exact) + 5 * len(expanded) + min(8, len(partial))
            if score == 0:
                continue
            score += 6 * sum(contains(heading, term) for term in primary)
            # A contiguous query match is more informative than scattered common tokens.
            if contains(body, normalize(query).strip()):
                score += 14
            matches = set(exact + expanded + partial)
            lines = content.splitlines()
            hit = next((i for i, line in enumerate(lines)
                        if any(contains(normalize(line), term) for term in matches)), 0)
            snippet = "\n".join(lines[max(0, hit - 1):hit + 7])[:1100]
            result.append({"path": doc["path"], "title": doc["title"], "section": title,
                           "line_start": start, "line_end": end, "score": score,
                           "evidence": doc["evidence"], "source_status": doc["source_status"],
                           "excerpt": snippet})
    return sorted(result, key=lambda hit: (-hit["score"], hit["path"], hit["line_start"]))[:limit]


def link_errors(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~", "", text, flags=re.S)
    errors = []
    for match in re.finditer(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
        target = match[1].strip()
        if target.startswith("<"):
            target = target[1:target.find(">")]
        else:
            target = target.split(' "', 1)[0]
        if urlsplit(target).scheme or target.startswith(("#", "//")):
            continue
        filename = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if filename and not (path.parent / filename).exists():
            errors.append(f"断链: {path}: {target}")
    return errors


def verify(root: Path):
    errors = []
    manifest = read_json(root / "manifest.json")
    if not manifest.get("files"):
        errors.append("原文清单为空")
    recorded = set()
    for item in manifest["files"]:
        recorded.add(item["path"])
        path = inside(root, item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            errors.append(f"原文快照与来源清单不一致: {item['path']}")
    actual = {p.relative_to(root).as_posix() for p in (root / "references" / "kd").glob("*.md")}
    if actual != recorded:
        errors.append("原文快照文件列表与清单不一致")
    if not (root / "catalog.json").exists() or read_json(root / "catalog.json") != build_catalog(root):
        errors.append("目录索引过期或缺失，请运行 index")
    for path in [*root.rglob("*.md"), *root.parent.glob("*.md"), *root.parent.glob("skills/*/SKILL.md")]:
        errors.extend(link_errors(path))
    glossary = read_json(root / "glossary.json")
    errors.extend(abbreviation_errors(glossary))
    table_path = root / "knowledge" / "name-crosswalk.md"
    if table_path.exists() and table_path.read_text(encoding="utf-8") != render_crosswalk(glossary):
        errors.append("简称对照表已过期，请运行 crosswalk，再运行 index")
    names = []
    for term in glossary["terms"]:
        names.append(term["term"])
        for ref in term.get("sources", []):
            if not inside(root, ref.split("#", 1)[0]).is_file():
                errors.append(f"术语出处缺失: {term['term']}: {ref}")
        for record in term.get("short_names", []):
            for ref in record.get("sources", []):
                if not inside(root, ref.split("#", 1)[0]).is_file():
                    errors.append(f"简称出处缺失: {term['term']}: {record['name']}: {ref}")
    if len(names) != len(set(names)):
        errors.append("术语表存在重复主词")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"校验通过: {len(recorded)} 份原文的 SHA-256、目录索引、本地文件链接、{len(names)} 个术语出处")
    print(f"简称/缩写字段校验通过: {sum(bool(term.get('abbreviation') or term.get('short_names')) for term in glossary['terms'])} 个概念")
    print("校验仅检查本地完整性，不验证外部链接、生产口径或技术事实；不会重签快照。")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="知识库source目录；默认从脚本真实路径定位")
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("snapshot", help="复制原始Markdown并记录SHA-256；不会删除历史文件")
    cmd.add_argument("--source", type=Path, required=True)
    cmd.add_argument("--update", action="store_true", help="审阅后允许覆盖发生变化的快照")
    cmd = sub.add_parser("index", help="更新文档目录与章节索引；不会改变原文清单")
    cmd.add_argument("--check", action="store_true")
    cmd = sub.add_parser("search", help="中英文字面检索、术语别名扩展；不使用远程服务")
    cmd.add_argument("query")
    cmd.add_argument("--category", choices=CATEGORIES)
    cmd.add_argument("--limit", type=int, default=5)
    cmd.add_argument("--json", action="store_true")
    cmd = sub.add_parser("abbr", help="按概念查询多个中文简称、英文缩写、数据集代号及其范围与证据")
    cmd.add_argument("query", nargs="?", default="")
    cmd.add_argument("--category", choices=ABBREVIATION_CATEGORIES)
    cmd.add_argument("--limit", type=int, default=200, help="最多返回1..200个概念，默认200")
    cmd.add_argument("--json", action="store_true")
    cmd = sub.add_parser("crosswalk", help="从术语主表生成可阅读的概念—多简称对照表")
    cmd.add_argument("--check", action="store_true")
    sub.add_parser("verify", help="校验快照、索引、本地文件链接和术语出处")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "snapshot":
            snapshot(root, args.source, args.update)
        elif args.command == "index":
            index(root, args.check)
        elif args.command == "verify":
            verify(root)
        elif args.command == "crosswalk":
            crosswalk(root, args.check)
        elif args.command == "abbr":
            terms = abbreviations(root, args.query, args.category, args.limit)
            disambiguation = name_disambiguation(root, args.query)
            if args.json:
                print(json.dumps({"query": args.query, "category": args.category,
                                  "count": len(terms), "results": terms,
                                  "disambiguation": disambiguation}, ensure_ascii=False, indent=2))
            elif not terms:
                print("当前查询/分类过滤下未找到名称映射；可换全称或取消分类过滤。")
                print(disambiguation["next_action"])
            else:
                if args.query:
                    print(f"上下文消歧: {disambiguation['status']}")
                    print(disambiguation["next_action"])
                    if disambiguation.get("confirmation_prompt"):
                        print("上下文仍不足时的提问示例: " + disambiguation["confirmation_prompt"])
                print(f"简称/缩写对照: {len(terms)} 个概念")
                for term in terms:
                    print(f"\n概念: {term['term']} | 中文: {term.get('chinese_full_name', term['term'])}")
                    if term.get("abbreviation"):
                        print(f"标准英文缩写/符号: {term['abbreviation']}")
                    if term.get("english_full_name"):
                        print(f"英文名称: {term['english_full_name']}")
                        basis = "原文明确展开" if term.get("full_name_status") == "source_explicit" else "整理补充的全称/译名"
                        print(f"英文名称依据: {basis}")
                    print(f"分类: {ABBREVIATION_CATEGORIES.get(term.get('category'), '未分类')} | 用途: {term.get('usage', '见含义和适用范围')}")
                    print(f"含义: {term.get('meaning', '')}")
                    for record in term.get("short_names", []):
                        note = "" if active_short_name(record) else "；不自动展开"
                        print(f"简称: {record['name']}（{NAME_KINDS[record['kind']]}；{NAME_STATUSES[record['status']]}{note}）")
                        print(f"  范围: {record['scope']}")
                        print("  证据: " + ", ".join(record["sources"]))
                    if term.get("notes"):
                        print(f"注意: {term['notes']}")
                    print(f"知识状态: {term.get('status', 'unknown')}")
                    print("出处: " + ", ".join(term.get("sources", [])))
        else:
            hits = search(root, args.query, args.category, args.limit)
            if args.json:
                print(json.dumps({"query": args.query, "results": hits}, ensure_ascii=False, indent=2))
            elif not hits:
                print("未命中。请换用设备名、缩写或原文关键词；未命中不等于不存在。")
            else:
                for hit in hits:
                    print(f"{hit['path']}:{hit['line_start']}-{hit['line_end']} [{hit['score']}] {hit['section']}")
                    if hit["source_status"] == "not_in_latest_import":
                        print("来源状态: 历史快照，未出现在最近一次上游导入中。")
                    print(hit["excerpt"] + "\n")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
