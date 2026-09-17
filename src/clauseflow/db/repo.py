from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import FieldExtraction
from .tables import DocumentRow, ExtractedFieldRow


async def upsert_document(
    session: AsyncSession, source_file: str, content_hash: str, full_text: str
) -> tuple[DocumentRow, bool]:
    existing = (
        await session.execute(select(DocumentRow).where(DocumentRow.content_hash == content_hash))
    ).scalar_one_or_none()
    if existing is not None:
        return existing, False
    row = DocumentRow(source_file=source_file, content_hash=content_hash, full_text=full_text)
    session.add(row)
    await session.flush()
    return row, True


async def replace_fields(
    session: AsyncSession, document_id: str, fields: list[FieldExtraction]
) -> None:
    await session.execute(
        delete(ExtractedFieldRow).where(ExtractedFieldRow.document_id == document_id)
    )
    for field in fields:
        session.add(
            ExtractedFieldRow(
                document_id=document_id,
                field_name=field.field,
                value=field.value,
                evidence_quote=field.evidence_quote,
                verified=field.evidence_quote is not None,
            )
        )
