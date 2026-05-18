from __future__ import annotations

from copy import deepcopy

from app.template_engine.instruction_rule_extractor import overlay_instruction_rules
from app.template_engine.template_conflict_detector import detect_conflicts


def merge_rules(sample_rules: dict, instruction_rules: dict) -> tuple[dict, list[dict], list[str]]:
    warnings: list[str] = []
    conflicts = detect_conflicts(instruction_rules, sample_rules)
    merged = overlay_instruction_rules(deepcopy(sample_rules), instruction_rules)
    for required in ["page", "body", "headings", "figures", "tables", "header_footer", "references"]:
        if required not in merged:
            warnings.append(f"缺少 {required} 规则，已使用默认值或等待用户确认。")
    return merged, conflicts, warnings
