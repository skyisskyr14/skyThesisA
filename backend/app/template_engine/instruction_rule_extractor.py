from __future__ import annotations

import re
from copy import deepcopy

from app.template_engine.utils import FONT_SIZE_MAP


def extract_instruction_rules(text: str) -> tuple[dict, list[dict]]:
    rules: dict = {}
    evidence: list[dict] = []
    compact = re.sub(r"\s+", "", text)

    body: dict = {}
    if "正文" in compact and "宋体" in compact:
        body["font_cn"] = "宋体"
        evidence.append(_ev("body.font_cn", "段落文本说明", "正文宋体"))
    size = _find_size_after(compact, "正文")
    if size:
        body["font_size_pt"] = size
        evidence.append(_ev("body.font_size_pt", "段落文本说明", f"正文字号 {size}pt"))
    if "首行缩进2字符" in compact or "首行缩进二字符" in compact:
        body["first_line_indent_chars"] = 2
        evidence.append(_ev("body.first_line_indent_chars", "段落文本说明", "正文首行缩进2字符"))
    line_spacing = re.search(r"行距([0-9.]+)倍", compact)
    if line_spacing:
        body["line_spacing"] = float(line_spacing.group(1))
        evidence.append(_ev("body.line_spacing", "段落文本说明", line_spacing.group(0)))
    if body:
        rules["body"] = body

    headings = []
    for label, level in [("一级标题", 1), ("二级标题", 2), ("三级标题", 3)]:
        if label in compact:
            heading: dict = {"level": level, "style_name": f"Heading {level}"}
            if "黑体" in compact[compact.find(label): compact.find(label) + 20]:
                heading["font_name"] = "黑体"
            heading_size = _find_size_after(compact, label)
            if heading_size:
                heading["font_size_pt"] = heading_size
            if "居中" in compact[compact.find(label): compact.find(label) + 30]:
                heading["alignment"] = "center"
            heading.setdefault("bold", False)
            heading.setdefault("numbering_pattern", "第{n}章" if level == 1 else "")
            headings.append(heading)
            evidence.append(_ev(f"headings[{level}]", "段落文本说明", label))
    if headings:
        rules["headings"] = headings

    figures: dict = {}
    if "图题在图下方" in compact or "图题置于图下" in compact:
        figures["caption_position"] = "below"
        evidence.append(_ev("figures.caption_position", "段落文本说明", "图题在图下方"))
    if figures:
        rules["figures"] = figures

    tables: dict = {}
    if "表题在表上方" in compact or "表题置于表上" in compact:
        tables["caption_position"] = "above"
        evidence.append(_ev("tables.caption_position", "段落文本说明", "表题在表上方"))
    if "三线表" in compact:
        tables["use_three_line_table"] = True
        evidence.append(_ev("tables.use_three_line_table", "段落文本说明", "表格采用三线表"))
    if tables:
        rules["tables"] = tables

    if "参考文献" in compact and "[1]" in compact:
        rules["references"] = {"numbering_style": "[1]", "heading_text": "参考文献"}
        evidence.append(_ev("references.numbering_style", "段落文本说明", "参考文献采用 [1] 编号"))
    return rules, evidence


def overlay_instruction_rules(base: dict, instruction_rules: dict) -> dict:
    merged = deepcopy(base)
    for key, value in instruction_rules.items():
        if key == "headings":
            by_level = {item.get("level"): item for item in merged.get("headings", [])}
            for instruction_heading in value:
                level = instruction_heading.get("level")
                target = by_level.setdefault(level, {"level": level})
                target.update(instruction_heading)
            merged["headings"] = sorted(by_level.values(), key=lambda item: item.get("level", 99))
        elif isinstance(value, dict):
            merged.setdefault(key, {}).update(value)
        else:
            merged[key] = value
    return merged


def _find_size_after(text: str, anchor: str) -> float | None:
    index = text.find(anchor)
    if index < 0:
        return None
    window = text[index: index + 30]
    for zh_size, pt in FONT_SIZE_MAP.items():
        if zh_size in window:
            return pt
    pt_match = re.search(r"([0-9.]+)磅", window)
    if pt_match:
        return float(pt_match.group(1))
    return None


def _ev(field: str, source: str, text: str) -> dict:
    return {"field": field, "source": source, "text": text}
