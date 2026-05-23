from __future__ import annotations

from app.template_engine.utils import safe_nested_get

FIELDS_TO_COMPARE = [
    "body.font_cn",
    "body.font_size_pt",
    "body.line_spacing",
    "body.first_line_indent_chars",
    "figures.caption_position",
    "tables.caption_position",
    "tables.use_three_line_table",
    "references.numbering_style",
]


def detect_conflicts(instruction_rules: dict, sample_rules: dict) -> list[dict]:
    conflicts: list[dict] = []
    for field in FIELDS_TO_COMPARE:
        instruction_value = safe_nested_get(instruction_rules, field)
        sample_value = safe_nested_get(sample_rules, field)
        if instruction_value is None or sample_value is None or instruction_value == sample_value:
            continue
        conflicts.append(
            {
                "field": field,
                "instruction_value": instruction_value,
                "sample_value": sample_value,
                "suggested_value": instruction_value,
                "reason": "说明文档规则优先于样例样式",
            }
        )
    instruction_headings = {item.get("level"): item for item in instruction_rules.get("headings", [])}
    sample_headings = {item.get("level"): item for item in sample_rules.get("headings", [])}
    for level, instruction_heading in instruction_headings.items():
        sample_heading = sample_headings.get(level)
        if not sample_heading:
            continue
        for name in ["font_name", "font_size_pt", "alignment"]:
            instruction_value = instruction_heading.get(name)
            sample_value = sample_heading.get(name)
            if instruction_value is not None and sample_value is not None and instruction_value != sample_value:
                conflicts.append(
                    {
                        "field": f"headings[level={level}].{name}",
                        "instruction_value": instruction_value,
                        "sample_value": sample_value,
                        "suggested_value": instruction_value,
                        "reason": "说明文档标题规则优先于样例样式",
                    }
                )
    return conflicts
