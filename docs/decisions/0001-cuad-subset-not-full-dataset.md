# 0001: Eval against a 7-contract CUAD subset, not all 510

## Context

CUAD v1 has 510 contracts across 41 clause categories. Running every category
against every contract needs 41x more LLM calls than a handful of the most
consistently-present fields, for categories present in only a few contracts
each.

## Decision

Pick 5 fields present in every one of a 7-contract sample (Document Name,
Parties, Effective Date, Expiration Date, Governing Law - verified by
counting non-impossible answers per category across the sample before
committing to it) and check in only those 7 real PDFs plus a filtered
annotations.json, not the full 40MB CUAD_v1.json.

## Consequences

Precision/recall numbers are real (drawn from the actual CUAD ground truth,
not synthetic data) but are not "CUAD benchmark" numbers in the sense a paper
would report - they're a curated slice chosen because it's fully populated,
not a random or representative sample. The README's results table says
"CUAD v1 subset (7 contracts)", never bare "CUAD", to keep that honest.
Extending to more fields or documents means re-running
`evals/build_verifier_pairs`-equivalent filtering against a freshly
downloaded CUAD_v1.json - the filtering logic lives in this decision record
since it was a one-off script, not committed code.
