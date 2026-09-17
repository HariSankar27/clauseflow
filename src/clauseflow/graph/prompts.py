from ..domain.models import FIELDS

EXTRACT_PROMPT = f"""Extract the following fields from the contract inside <contract> tags:
{", ".join(FIELDS)}.

For each field, if the contract states it, give the value and copy the exact sentence or
phrase from the contract that supports it verbatim into evidence_quote. If the contract does
not state a field, set both value and evidence_quote to null. Never paraphrase evidence_quote -
it must be copyable, verbatim text from the contract.

<contract>{{contract_text}}</contract>"""
