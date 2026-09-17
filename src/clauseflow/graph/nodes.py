from pathlib import Path

from ..domain.models import ExtractedFields, FieldExtraction
from ..llm import chat_model
from ..parse.docling_parser import parse_pdf
from .prompts import EXTRACT_PROMPT
from .state import PipelineState


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def parse_document(state: PipelineState) -> dict:
    text, content_hash = parse_pdf(state["pdf_path"])
    return {
        "document_text": text,
        "content_hash": content_hash,
        "source_file": Path(state["pdf_path"]).name,
    }


async def extract_fields(state: PipelineState) -> dict:
    llm = chat_model().with_structured_output(ExtractedFields)
    result = await llm.ainvoke(EXTRACT_PROMPT.format(contract_text=state["document_text"]))
    return {"fields": [f.model_dump() for f in result.fields]}


def verify_field(field: FieldExtraction, document_text: str) -> FieldExtraction:
    """Drops a field's value/evidence unless the evidence is a real, verbatim
    quote from the document - the same "no source, no claim" rule as jobpilot's
    filter_verified_requirements, applied to clause extraction instead."""
    if field.evidence_quote is None:
        return FieldExtraction(field=field.field, value=None, evidence_quote=None)
    if _norm(field.evidence_quote) in _norm(document_text):
        return field
    return FieldExtraction(field=field.field, value=None, evidence_quote=None)


def verify_evidence(state: PipelineState) -> dict:
    verified = [
        verify_field(FieldExtraction(**f), state["document_text"]).model_dump()
        for f in state["fields"]
    ]
    return {"fields": verified}
