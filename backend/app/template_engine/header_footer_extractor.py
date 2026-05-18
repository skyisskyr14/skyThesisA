from __future__ import annotations

from docx.document import Document as DocxDocument


def extract_header_footer_rules(document: DocxDocument) -> tuple[dict, list[dict]]:
    headers: list[str] = []
    footers: list[str] = []
    for section in document.sections:
        headers.extend([p.text.strip() for p in section.header.paragraphs if p.text.strip()])
        footers.extend([p.text.strip() for p in section.footer.paragraphs if p.text.strip()])
    footer_text = " ".join(footers)
    header_text = " ".join(headers)
    rules = {
        "has_header": bool(header_text),
        "header_text": header_text,
        "has_footer": bool(footer_text),
        "footer_text": footer_text,
        "has_page_number": any(token in footer_text + header_text for token in ["PAGE", "页", "第", "共"]),
    }
    evidence = [{"field": "header_footer", "source": "sections.header/footer", "text": f"页眉：{header_text[:40]} 页脚：{footer_text[:40]}"}]
    return rules, evidence
