#!/usr/bin/env python3
"""Build README comparison diagrams from the maintained scenario descriptions."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import struct
import unicodedata
from xml.sax.saxutils import escape

DOCS = Path(__file__).resolve().parents[1]
FONT = "Microsoft YaHei, Noto Sans CJK SC, Arial, sans-serif"


def wrap(value: str, width: float, size: int):
    lines, current, used = [], "", 0.0
    for char in value:
        advance = size * (1.0 if unicodedata.east_asian_width(char) in "WF" else 0.58)
        if current and used + advance > width:
            lines.append(current)
            current, used = "", 0.0
        current += char
        used += advance
    if current:
        lines.append(current)
    return lines


def text(x, y, value, size=20, fill="#1f354b", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{escape(str(value))}</text>'


def paragraph(x, y, value, width, size=20, fill="#1f354b", weight="400", max_lines=2):
    lines = wrap(value, width, size)
    if len(lines) > max_lines:
        raise ValueError(f"Diagram text exceeds {max_lines} lines: {value}")
    return "\n".join(text(x, y + index * (size + 8), line, size, fill, weight)
                     for index, line in enumerate(lines))


def diagram(item: dict, number: int):
    if not re.fullmatch(r"[a-z][a-z0-9-]+", item["id"]):
        raise ValueError(f"Invalid diagram id: {item['id']}")
    if len(item["before"]) != 3 or len(item["after"]) != 3:
        raise ValueError("Each comparison must have three readable observations per side")
    title = f"{number:02d}  {item['title']}"
    has_preview = bool(item.get("preview_before") and item.get("preview_after"))
    height = 1020 if has_preview else 660
    card_height = 690 if has_preview else 330
    footer_y = 912 if has_preview else 552
    caption_y = 1002 if has_preview else 642
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="{height}" viewBox="0 0 1280 {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(item["title"])}：使用与未使用项目 skill 的对比示意</title>',
        f'<desc id="desc">同一任务：{escape(item["scenario"])}。未使用：{escape("；".join(item["before"]))}。使用：{escape("；".join(item["after"]))}。{escape(item["outcome"])}。这是工作方式示意，没有量化评测结论。</desc>',
        f'<rect width="1280" height="{height}" rx="24" fill="#f3f6fb"/>',
        f'<g font-family="{FONT}">',
        paragraph(48, 54, title, 950, 28, "#142b43", "700", 1),
        text(48, 88, item["dimension"], 17, "#526b81"),
        '<rect x="1062" y="30" width="170" height="35" rx="17" fill="#e5edf7"/>',
        text(1085, 53, "具体任务示例", 17, "#526b81"),
        '<rect x="48" y="112" width="1184" height="59" rx="12" fill="#fff" stroke="#d6e0eb"/>',
        text(68, 148, "同一个任务", 18, "#526b81", "700"),
        paragraph(186, 148, item["scenario"], 1015, 19, "#1f354b", max_lines=1),
    ]
    for x, field, heading, subtitle, accent, tint in (
        (48, "before", "未使用本项目 skill", "依赖通用能力与本次提示", "#64748b", "#edf1f6"),
        (664, "after", "使用对应 skill", "增加业务知识与规范流程", "#0f766e", "#e5f4ef"),
    ):
        elements.extend([
            f'<rect x="{x}" y="198" width="568" height="{card_height}" rx="18" fill="#fff" stroke="{accent}" stroke-opacity="0.3"/>',
            f'<path d="M{x + 18} 198H{x + 550}" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>',
            text(x + 28, 241, heading, 23, accent, "700"),
            text(x + 28, 272, item.get(f"{field}_caption", subtitle), 16, "#64748b"),
            f'<line x1="{x + 28}" y1="291" x2="{x + 540}" y2="291" stroke="#e3eaf2"/>',
        ])
        for index, observation in enumerate(item[field]):
            y = 330 + index * 67
            elements.extend([
                f'<rect x="{x + 26}" y="{y - 24}" width="32" height="32" rx="9" fill="{tint}"/>',
                text(x + 36, y - 1, index + 1, 17, accent, "700"),
                paragraph(x + 76, y, observation, 464, 21, "#243d54", max_lines=2),
            ])
        if has_preview:
            preview = DOCS / item[f"preview_{field}"]
            pixels = preview.read_bytes()
            if not pixels.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError(f"Preview must be PNG: {preview}")
            width, full_height = struct.unpack('>II', pixels[16:24])
            crop_height = round(full_height * item.get("preview_crop_fraction", 1))
            data = base64.b64encode(pixels).decode("ascii")
            elements.extend([
                f'<rect x="{x + 26}" y="540" width="516" height="324" rx="10" fill="#f8fafc" stroke="#d6e0eb"/>',
                f'<svg x="{x + 34}" y="548" width="500" height="308" viewBox="0 0 {width} {crop_height}" overflow="hidden">',
                f'<image width="{width}" height="{full_height}" href="data:image/png;base64,{data}"/>',
                '</svg>',
            ])
    elements.extend([
        f'<rect x="48" y="{footer_y}" width="1184" height="61" rx="14" fill="#142b43"/>',
        text(72, footer_y + 37, "本例可见", 18, "#c6d7e7", "700"),
        paragraph(184, footer_y + 38, item["outcome"], 1014, 21, "#fff", "600", 1),
        text(48, caption_y, item.get("example_note", "回答摘要与完整示例相互对应；仅展示本次任务，不代表量化准确率或效果保证。"), 15, "#64748b"),
        '</g>', '</svg>', '',
    ])
    return "\n".join(elements)


def casebook(scenarios):
    before = json.loads((DOCS / 'examples/baseline-answers.json').read_text(encoding='utf-8-sig'))
    after = json.loads((DOCS / 'examples/skill-answers.json').read_text(encoding='utf-8-sig'))
    before_tasks = {task['id']: task for task in before['tasks']}
    after_tasks = {task['id']: task for task in after['tasks']}
    lines = ['# 同一输入的实际回答示例', '',
             '一侧按要求未读取本项目 skills、知识库或外网；另一侧读取相应 skill 和本地依据。由不同 Agent 完成的一次回答，输入保持一致。',
             '以下保留完整原文。它们是可审阅案例，不是严格的模型 A/B 性能评测；没有重复试验、盲评或准确率统计。',
             '部分问题两侧都给出正确或审慎的结论，图示如实保留这些一致点。', '',
             '原始记录：[未使用项目 skill](baseline-answers.json) · [使用项目 skill](skill-answers.json)', '']
    for scenario in scenarios:
        key = scenario.get('example_id')
        if not key:
            continue
        left, right = before_tasks[key], after_tasks[key]
        if left['input'] != right['input']:
            raise ValueError(f'Comparison inputs differ: {key}')
        lines.extend([f'<a id="{key}"></a>', '', f"## {scenario['title']}", '',
                      '**相同输入**', '', left['input'], '',
                      '**未使用本项目 skill：原始回答**', '', left['answer'], '',
                      f"**使用 {right['skill']}：原始回答**", '', right['answer'], '',
                      '**本例可见的差异**', '', scenario['outcome'] + '。', '', '**使用侧的本地依据**', ''])
        for ref in right.get('evidence', []):
            # Captured answers retain the original host path as provenance.
            # Resolve project-local evidence against this checkout for portability.
            parts = ref.replace('\\', '/').split('/')
            path = Path(ref).resolve()
            for anchor in ('source', 'skills'):
                if anchor in parts:
                    local = DOCS.parent.joinpath(*parts[parts.index(anchor):])
                    if local.is_file():
                        path = local.resolve()
                        break
            if not path.exists():
                raise ValueError(f'Example evidence is missing: {path}')
            link = os.path.relpath(path, DOCS / 'examples').replace('\\', '/')
            lines.append(f'- [{path.name}]({link})')
        lines.append('')
    return '\n'.join(lines)


def build(check: bool = False):
    content = json.loads((DOCS / "comparison-scenarios.json").read_text(encoding="utf-8-sig"))
    scenarios = content["scenarios"]
    ids = [item["id"] for item in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate comparison diagram ids")
    output = DOCS / "images"
    output.mkdir(exist_ok=True)
    for number, item in enumerate(scenarios, 1):
        target = output / f"compare-{item['id']}.svg"
        expected = diagram(item, number)
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                raise ValueError(f"Comparison diagram is stale: {target}")
        else:
            target.write_text(expected, encoding="utf-8")
    if (DOCS / 'examples/baseline-answers.json').exists() and (DOCS / 'examples/skill-answers.json').exists():
        target = DOCS / 'examples/agent-comparison.md'
        expected = casebook(scenarios)
        if check:
            if not target.exists() or target.read_text(encoding='utf-8') != expected:
                raise ValueError(f'Example casebook is stale: {target}')
        else:
            target.write_text(expected, encoding='utf-8')
    print(f"{'Checked' if check else 'Generated'} {len(scenarios)} comparison diagrams")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    build(parser.parse_args().check)
