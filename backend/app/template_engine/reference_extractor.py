from __future__ import annotations

import re

from docx.document import Document as DocxDocument


def extract_reference_rules(document: DocxDocument) -> tuple[dict, list[dict]]:
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    heading = next((text for text in paragraphs if text in {"参考文献", "References"}), "")
    samples = [text for text in paragraphs if re.match(r"\[\d+\]", text)][:5]
    numbering_style = "[1]" if samples else "unknown"
    rules = {"heading_text": heading or "参考文献", "numbering_style": numbering_style, "samples": samples}
    evidence = []
    if heading:
        evidence.append({"field": "references.heading_text", "source": "段落文本", "text": heading})
    if samples:
        evidence.append({"field": "references.samples", "source": "参考文献段落", "text": samples[0]})
    return rules, evidence
