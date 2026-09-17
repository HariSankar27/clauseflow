import pytest
from sqlalchemy import select

from clauseflow.db.repo import replace_fields, upsert_document
from clauseflow.db.session import async_session
from clauseflow.db.tables import ExtractedFieldRow
from clauseflow.domain.models import FieldExtraction

pytestmark = pytest.mark.integration


async def test_upsert_document_is_idempotent_on_content_hash():
    async with async_session() as session:
        first, created1 = await upsert_document(session, "a.pdf", "hash-repo-test", "full text")
        second, created2 = await upsert_document(session, "a.pdf", "hash-repo-test", "full text")
        await session.commit()

    assert created1 is True
    assert created2 is False
    assert first.id == second.id


async def test_replace_fields_marks_verified_by_presence_of_evidence():
    async with async_session() as session:
        document, _ = await upsert_document(session, "b.pdf", "hash-repo-fields", "text")
        fields = [
            FieldExtraction(field="Document Name", value="X", evidence_quote="X"),
            FieldExtraction(field="Governing Law", value=None, evidence_quote=None),
        ]
        await replace_fields(session, document.id, fields)
        await session.commit()

        rows = (
            (
                await session.execute(
                    select(ExtractedFieldRow).where(ExtractedFieldRow.document_id == document.id)
                )
            )
            .scalars()
            .all()
        )

    verified_by_name = {r.field_name: r.verified for r in rows}
    assert verified_by_name == {"Document Name": True, "Governing Law": False}
