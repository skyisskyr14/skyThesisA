from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULT_TEMPLATE_RULES: dict[str, Any] = {
    "page": {
        "paper_size": "A4",
        "width_cm": 21.0,
        "height_cm": 29.7,
        "margin_top_cm": 2.5,
        "margin_bottom_cm": 2.5,
        "margin_left_cm": 2.5,
        "margin_right_cm": 2.5,
    },
    "body": {
        "font_cn": "宋体",
        "font_en": "Times New Roman",
        "font_size_pt": 12,
        "line_spacing": 1.25,
        "first_line_indent_chars": 2,
        "alignment": "justify",
        "space_before_pt": 0,
        "space_after_pt": 0,
    },
    "headings": [
        {"level": 1, "font_name": "黑体", "font_size_pt": 16, "bold": False, "alignment": "center", "space_before_pt": 12, "space_after_pt": 12, "numbering_pattern": "第{n}章"},
        {"level": 2, "font_name": "黑体", "font_size_pt": 15, "bold": False, "alignment": "left", "space_before_pt": 6, "space_after_pt": 6, "numbering_pattern": "{chapter}.{n}"},
        {"level": 3, "font_name": "黑体", "font_size_pt": 14, "bold": False, "alignment": "left", "space_before_pt": 6, "space_after_pt": 6, "numbering_pattern": "{chapter}.{section}.{n}"},
    ],
    "figures": {"caption_position": "below", "caption_pattern": "图{chapter}-{index} {title}", "font_name": "宋体", "font_size_pt": 10.5, "alignment": "center"},
    "tables": {"caption_position": "above", "caption_pattern": "表{chapter}-{index} {title}", "use_three_line_table": True, "font_name": "宋体", "font_size_pt": 10.5, "alignment": "center", "cell_alignment": "center"},
    "header_footer": {"has_header": True, "header_text": "", "has_footer": True, "footer_text": "", "has_page_number": True},
    "references": {"heading_text": "参考文献", "numbering_style": "[1]"},
}

REQUIRED_PATHS = [
    "page.margin_top_cm", "page.margin_bottom_cm", "page.margin_left_cm", "page.margin_right_cm",
    "body.font_cn", "body.font_size_pt", "body.line_spacing", "body.first_line_indent_chars",
    "figures.caption_position", "tables.caption_position", "tables.use_three_line_table",
    "header_footer.has_header", "references.numbering_style",
]


def resolve_template_rules(template_rules: dict[str, Any] | None) -> tuple[dict[str, Any], list[str], list[str], bool]:
    used_template_rules = bool(template_rules)
    resolved = deepcopy(DEFAULT_TEMPLATE_RULES)
    missing: list[str] = []
    applied: list[str] = []
    template_rules = template_rules or {}
    for path in REQUIRED_PATHS:
        value = _get(template_rules, path)
        if value is None:
            missing.append(path)
        else:
            _set(resolved, path, value)
            applied.append(path)
    for key in ["page", "body", "figures", "tables", "header_footer", "references"]:
        if isinstance(template_rules.get(key), dict):
            resolved[key].update(template_rules[key])
    if template_rules.get("headings"):
        by_level = {h["level"]: h for h in resolved["headings"]}
        for heading in template_rules["headings"]:
            level = heading.get("level")
            if level:
                by_level[level].update(heading)
                applied.append(f"headings.level_{level}")
        resolved["headings"] = sorted(by_level.values(), key=lambda h: h["level"])
    return resolved, sorted(set(applied)), missing, used_template_rules


def heading_rule(rules: dict[str, Any], level: int) -> dict[str, Any]:
    for heading in rules.get("headings", []):
        if heading.get("level") == level:
            return heading
    return DEFAULT_TEMPLATE_RULES["headings"][min(level - 1, 2)]


def _get(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _set(data: dict[str, Any], path: str, value: Any) -> None:
    current = data
    parts = path.split(".")
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value
