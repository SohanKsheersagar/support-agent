"""Opt-in live smoke evals with fictional questions; not full harness acceptance."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path

import psycopg

from app.orchestrator.rag import draft_from_evidence
from app.retrieval.embeddings import Embedder
from app.retrieval.search import search_kb


def run() -> tuple[Path, bool]:
    directory = Path(__file__).resolve().parent
    cases = json.loads((directory / "rag_cases.json").read_text())
    encoder = Embedder()
    results = []
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as connection:
        for case in cases:
            passages = search_kb(connection, encoder, case["question"], top_k=5)
            result = draft_from_evidence(case["question"], passages)
            passed = result.route == case["expected_route"]
            if case["expected_source"]:
                passed = passed and case["expected_source"] in {
                    citation["source_id"] for citation in result.citations
                }
            else:
                passed = passed and result.draft is None and result.reason in {
                    "insufficient_evidence_or_human_required", "grounding_check_failed"
                }
            results.append({
                **case, "passed": passed, "retrieved_sources": [p["source_id"] for p in passages],
                "result": result.model_dump(),
            })
            print(f"{case['id']}: {'PASS' if passed else 'FAIL'} ({result.reason})", flush=True)
    path = directory / "results" / datetime.now(timezone.utc).strftime("rag-%Y%m%dT%H%M%S%fZ.json")
    path.write_text(json.dumps({
        "passed": sum(r["passed"] for r in results), "total": len(results),
        "scope": "Routing and citation smoke checks; factual quality requires human review",
        "cases": results,
    }, indent=2) + "\n")
    return path, all(result["passed"] for result in results)


if __name__ == "__main__":
    report, passed = run()
    print(f"Report: {report}")
    raise SystemExit(0 if passed else 1)
