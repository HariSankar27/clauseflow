import asyncio

import typer

from .db.repo import replace_fields, upsert_document
from .db.session import async_session
from .domain.models import FieldExtraction
from .graph.build import build_graph

app = typer.Typer()


@app.command()
def extract(pdf_path: str) -> None:
    """Parses a contract PDF, extracts fields with evidence, and stores the result."""

    async def _run() -> None:
        graph = build_graph()
        result = await graph.ainvoke({"pdf_path": pdf_path})
        fields = [FieldExtraction(**f) for f in result["fields"]]

        async with async_session() as session:
            document, _ = await upsert_document(
                session, result["source_file"], result["content_hash"], result["document_text"]
            )
            await replace_fields(session, document.id, fields)
            await session.commit()

        for field in fields:
            if field.value is None:
                typer.echo(f"[MISSING] {field.field}")
            else:
                typer.echo(f"[OK] {field.field}: {field.value}")
                typer.echo(f'         evidence: "{field.evidence_quote}"')

    asyncio.run(_run())


if __name__ == "__main__":
    app()
