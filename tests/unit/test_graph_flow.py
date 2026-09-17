from pathlib import Path

import pytest

from clauseflow.domain.models import ExtractedFields, FieldExtraction
from clauseflow.graph import nodes as nodes_module
from clauseflow.graph.build import build_graph

FIXTURE_PDF = (
    Path(__file__).parent.parent.parent
    / "evals/datasets/contracts/pdf"
    / "LinkPlusCorp_20050802_8-K_EX-10_3240252_EX-10_Affiliate_Agreement.pdf"
)


class _FakeStructured:
    def __init__(self, result):
        self._result = result

    async def ainvoke(self, prompt: str):
        return self._result


class _FakeChatModel:
    def __init__(self, result):
        self._result = result

    def with_structured_output(self, schema):
        return _FakeStructured(self._result)


@pytest.mark.skipif(not FIXTURE_PDF.exists(), reason="eval fixture PDF not present")
async def test_full_pipeline_parses_real_pdf_and_verifies_evidence(monkeypatch):
    drafted = ExtractedFields(
        fields=[
            FieldExtraction(
                field="Document Name", value="Real", evidence_quote="AFFILIATE AGREEMENT"
            ),
            FieldExtraction(
                field="Governing Law",
                value="Nowhere",
                evidence_quote="laws of the state of Atlantis",
            ),
        ]
    )
    monkeypatch.setattr(nodes_module, "chat_model", lambda *a, **k: _FakeChatModel(drafted))

    graph = build_graph()
    result = await graph.ainvoke({"pdf_path": str(FIXTURE_PDF)})

    assert len(result["document_text"]) > 100
    by_field = {f["field"]: f for f in result["fields"]}
    assert by_field["Document Name"]["value"] == "Real"  # real quote from the PDF
    assert by_field["Governing Law"]["value"] is None  # hallucinated quote, dropped
