"""Scores clauseflow against a 7-contract subset of CUAD v1 (see
evals/datasets/contracts/annotations.json). For each of the 5 extracted
fields, counts a hit when the predicted value and a ground-truth answer
overlap (case-insensitive substring either direction) - exact-string match
is too strict for free-text span answers. Reports precision and recall,
writes a dated results file, and regenerates the README results table.
"""

import argparse
import asyncio
import json
import re
import time
from datetime import date
from pathlib import Path

from clauseflow.graph.build import build_graph

ANNOTATIONS_PATH = Path("evals/datasets/contracts/annotations.json")
PDF_DIR = Path("evals/datasets/contracts/pdf")
RESULTS_DIR = Path("evals/results")
README_PATH = Path("README.md")
README_MARKERS = ("<!-- eval-results:start -->", "<!-- eval-results:end -->")


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _is_hit(predicted: str | None, answers: list[str]) -> bool:
    if predicted is None or not answers:
        return False
    predicted_n = _norm(predicted)
    return any(_norm(a) in predicted_n or predicted_n in _norm(a) for a in answers)


async def score_document(pdf_path: Path, expected_fields: dict[str, list[str]]) -> dict:
    graph = build_graph()
    result = await graph.ainvoke({"pdf_path": str(pdf_path)})
    predicted_by_field = {f["field"]: f["value"] for f in result["fields"]}

    outcomes = []
    for field, answers in expected_fields.items():
        predicted = predicted_by_field.get(field)
        hit = _is_hit(predicted, answers)
        outcomes.append({"field": field, "predicted": predicted, "answers": answers, "hit": hit})
    return {"pdf": pdf_path.name, "outcomes": outcomes}


async def run_eval_suite(entries: list[dict]) -> dict:
    per_document = []
    for entry in entries:
        pdf_path = PDF_DIR / entry["pdf"]
        per_document.append(await score_document(pdf_path, entry["fields"]))

    all_outcomes = [o for doc in per_document for o in doc["outcomes"]]
    total = len(all_outcomes)
    hits = sum(1 for o in all_outcomes if o["hit"])
    predicted_non_null = sum(1 for o in all_outcomes if o["predicted"] is not None)

    return {
        "precision": hits / predicted_non_null if predicted_non_null else None,
        "recall": hits / total if total else None,
        "documents": len(entries),
        "fields_scored": total,
        "per_document": per_document,
    }


def regenerate_readme_table(metrics: dict) -> None:
    start, end = README_MARKERS
    text = README_PATH.read_text()
    header = (
        "| Metric | Value | Model | Dataset | Trials | Date |\n"
        "|--------|-------|-------|---------|--------|------|"
    )
    dataset = f"CUAD v1 subset ({metrics['documents']} contracts)"
    row_fmt = "| {name} | {value} | {model} | {dataset} | {trials} | {date} |"
    rows = "\n".join(
        row_fmt.format(
            name=name,
            value=metrics[name],
            model=metrics["model"],
            dataset=dataset,
            trials=metrics["fields_scored"],
            date=metrics["date"],
        )
        for name in ("precision", "recall")
    )
    table = f"{start}\n{header}\n{rows}\n{end}"
    new_text = re.sub(f"{re.escape(start)}.*?{re.escape(end)}", table, text, flags=re.DOTALL)
    README_PATH.write_text(new_text)


def main() -> None:
    from clauseflow.settings import settings

    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=["smoke", "full"], default="full")
    args = parser.parse_args()

    entries = json.loads(ANNOTATIONS_PATH.read_text())
    if args.suite == "smoke":
        entries = entries[:2]

    start = time.monotonic()
    metrics = asyncio.run(run_eval_suite(entries))
    metrics["latency_s"] = round(time.monotonic() - start, 2)
    metrics["model"] = settings.llm_model
    metrics["date"] = date.today().isoformat()
    metrics["suite"] = args.suite

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / f"{metrics['date']}.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_document"}, indent=2))

    regenerate_readme_table(metrics)


if __name__ == "__main__":
    main()
