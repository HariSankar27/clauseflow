import hashlib
from pathlib import Path


def parse_pdf(pdf_path: str | Path) -> tuple[str, str]:
    """Converts a PDF to plain text with Docling. Returns (text, content_hash).

    ponytail: lazy import - Docling pulls in torch/transformers for its layout
    model, so importing it only when actually parsing keeps `clauseflow --help`
    and anything not touching a PDF fast to start.
    """
    from docling.document_converter import DocumentConverter

    result = DocumentConverter().convert(str(pdf_path))
    text = result.document.export_to_text()
    content_hash = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
    return text, content_hash
