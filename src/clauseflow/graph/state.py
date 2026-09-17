from typing import TypedDict


class PipelineState(TypedDict, total=False):  # JSON-friendly values only
    pdf_path: str
    source_file: str
    document_text: str
    content_hash: str
    fields: list[dict]
