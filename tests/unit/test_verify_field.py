from clauseflow.domain.models import FieldExtraction
from clauseflow.graph.nodes import verify_field

DOCUMENT = "This Agreement is governed by the laws of the State of Delaware."


def test_keeps_field_with_verbatim_evidence():
    field = FieldExtraction(
        field="Governing Law", value="Delaware", evidence_quote="laws of the State of Delaware"
    )
    assert verify_field(field, DOCUMENT) == field


def test_drops_field_with_hallucinated_evidence():
    field = FieldExtraction(
        field="Governing Law", value="California", evidence_quote="laws of the State of California"
    )
    result = verify_field(field, DOCUMENT)
    assert result.value is None
    assert result.evidence_quote is None


def test_passes_through_a_field_with_no_evidence_as_missing():
    field = FieldExtraction(field="Expiration Date", value=None, evidence_quote=None)
    result = verify_field(field, DOCUMENT)
    assert result.value is None


def test_evidence_match_is_case_and_whitespace_insensitive():
    field = FieldExtraction(
        field="Governing Law", value="Delaware", evidence_quote="LAWS  of the state OF Delaware"
    )
    assert verify_field(field, DOCUMENT).value == "Delaware"


async def test_oversized_document_is_truncated_with_a_warning(monkeypatch, caplog):
    import logging

    from clauseflow.domain.models import ExtractedFields
    from clauseflow.graph import nodes as nodes_module

    seen = {}

    class _Structured:
        async def ainvoke(self, prompt: str):
            seen["prompt_len"] = len(prompt)
            return ExtractedFields(fields=[])

    class _Chat:
        def with_structured_output(self, schema):
            return _Structured()

    monkeypatch.setattr(nodes_module, "chat_model", lambda *a, **k: _Chat())
    monkeypatch.setattr(nodes_module.settings, "max_document_chars", 100)

    with caplog.at_level(logging.WARNING):
        await nodes_module.extract_fields({"document_text": "x" * 5000})

    assert seen["prompt_len"] < 5000
    assert "reported missing" in caplog.text
