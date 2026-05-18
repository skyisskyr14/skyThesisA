from __future__ import annotations

from typing import Any

FONT_SIZE_MAP = {
    "初号": 42,
    "小初": 36,
    "一号": 26,
    "小一": 24,
    "二号": 22,
    "小二": 18,
    "三号": 16,
    "小三": 15,
    "四号": 14,
    "小四": 12,
    "五号": 10.5,
    "小五": 9,
}


def cm_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value.cm), 2)
    except Exception:
        return None


def pt_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value.pt), 2)
    except Exception:
        return None


def alignment_name(value: Any) -> str | None:
    if value is None:
        return None
    name = getattr(value, "name", None)
    if not name:
        return str(value)
    mapping = {
        "LEFT": "left",
        "CENTER": "center",
        "RIGHT": "right",
        "JUSTIFY": "justify",
        "DISTRIBUTE": "distribute",
    }
    return mapping.get(name, name.lower())


def get_font_name(run_or_style: Any) -> str | None:
    font = getattr(run_or_style, "font", None)
    if font is not None and font.name:
        return font.name
    try:
        rfonts = run_or_style._element.rPr.rFonts
        return rfonts.get(qn("w:eastAsia")) or rfonts.get(qn("w:ascii"))
    except Exception:
        return None


def safe_nested_get(data: dict, path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


# qn 仅在 get_font_name 的高级 OOXML 路径中需要，放在末尾避免普通测试强依赖导入顺序。
try:
    from docx.oxml.ns import qn
except Exception:  # pragma: no cover - 仅用于未安装 python-docx 时的静态导入兜底
    def qn(value: str) -> str:
        return value
