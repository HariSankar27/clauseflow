from pydantic import BaseModel

FIELDS: list[str] = [
    "Document Name",
    "Parties",
    "Effective Date",
    "Expiration Date",
    "Governing Law",
]


class FieldExtraction(BaseModel):
    field: str
    value: str | None = None
    evidence_quote: str | None = None


class ExtractedFields(BaseModel):
    fields: list[FieldExtraction]


class ContractRecord(BaseModel):
    source_file: str
    fields: list[FieldExtraction]
