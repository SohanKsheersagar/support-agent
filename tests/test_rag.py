from unittest.mock import MagicMock, Mock, patch
from types import SimpleNamespace
import json

from google.genai import errors
import pytest

from app.gateway.gemini import GatewayError, complete
from app.orchestrator.rag import Candidate, GroundingCheck, draft_from_evidence
from app.orchestrator.rag import RagResult

PASSAGE = {
    "source_id": "KB-CARE-001", "title": "Washing a sleeping bag",
    "text": "Use a front-loading machine and dry on low heat.",
    "version": "test-version", "audience": "public",
}


def candidate(**changes):
    return Candidate.model_validate({
        "answerable": True, "draft": "Use a front-loading machine and dry on low heat.",
        "citations": [{"source_id": "KB-CARE-001", "quote": "Use a front-loading machine"}],
        "reason": "Supported by supplied passage", **changes,
    })


def test_grounded_draft_is_for_human_review_only():
    generate = Mock(side_effect=[
        (candidate(), {"tokens_total": 50}),
        (GroundingCheck(supported=True, reason="Supported"), {"tokens_total": 30}),
    ])
    result = draft_from_evidence("How do I wash it?", [PASSAGE], generate)
    assert result.route == "human_review"
    assert result.citations[0]["version"] == "test-version"
    assert len(result.calls) == 2
    assert generate.call_count == 2


def test_no_public_evidence_skips_model():
    generate = Mock()
    for passages in ([], [{**PASSAGE, "audience": "internal"}]):
        result = draft_from_evidence("Question", passages, generate)
        assert result.route == "escalate_to_human"
        assert result.draft is None
    generate.assert_not_called()


@pytest.mark.parametrize("draft,reason", [
    (candidate(answerable=False, draft="", citations=[]), "insufficient_evidence_or_human_required"),
    (candidate(citations=[]), "missing_draft_or_citations"),
    (candidate(citations=[{"source_id": "invented", "quote": "Use a front-loading machine"}]), "invalid_citation"),
    (candidate(citations=[{"source_id": "KB-CARE-001", "quote": "Invented supporting quote"}]), "invalid_citation"),
    (candidate(draft="It will definitely be fine."), "forbidden_promise"),
])
def test_rejected_draft_never_reaches_reviewer(draft, reason):
    generate = Mock(return_value=(draft, {}))
    result = draft_from_evidence("Question", [PASSAGE], generate)
    assert result.route == "escalate_to_human"
    assert result.draft is None
    assert result.reason == reason
    generate.assert_called_once()


def test_valid_quote_does_not_override_failed_grounding():
    generate = Mock(side_effect=[
        (candidate(draft="Your refund is approved."), {}),
        (GroundingCheck(supported=False, reason="Unsupported financial claim"), {}),
    ])
    result = draft_from_evidence("Question", [PASSAGE], generate)
    assert result.draft is None
    assert result.reason == "grounding_check_failed"


def test_provider_failure_escalates_without_retry():
    generate = Mock(side_effect=GatewayError("provider_error_429"))
    result = draft_from_evidence("Question", [PASSAGE], generate)
    assert result.route == "escalate_to_human"
    assert result.draft is None
    generate.assert_called_once()


def test_gateway_validates_output_and_does_not_expose_provider_messages(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    with patch("app.gateway.gemini.genai.Client") as factory:
        client = factory.return_value.__enter__.return_value
        client.models.generate_content.return_value = SimpleNamespace(
            text='{"supported":true,"reason":"Supported"}', usage_metadata=None
        )
        output, usage = complete("Check", {}, GroundingCheck)
        assert output.supported is True
        assert usage["model"] == "test-model"
        assert factory.call_args.kwargs["http_options"].retry_options.attempts == 1
        client.models.generate_content.return_value.text = '{"supported":"not-a-bool"}'
        with pytest.raises(GatewayError, match="provider_or_output_failure"):
            complete("Check", {}, GroundingCheck)
        client.models.generate_content.side_effect = errors.ClientError(
            429, {"error": {"message": "private provider details"}}
        )
        with pytest.raises(GatewayError) as caught:
            complete("Check", {}, GroundingCheck)
        assert str(caught.value) == "provider_error_429"


def test_live_report_does_not_count_provider_failure_as_correct_abstention(tmp_path, monkeypatch):
    from evals import run_rag

    (tmp_path / "results").mkdir()
    (tmp_path / "rag_cases.json").write_text(json.dumps([{
        "id": "unknown", "question": "Unknown policy?",
        "expected_route": "escalate_to_human", "expected_source": None,
    }]))
    monkeypatch.setattr(run_rag, "__file__", str(tmp_path / "run_rag.py"))
    monkeypatch.setenv("DATABASE_URL", "test-database")
    monkeypatch.setattr(run_rag, "Embedder", Mock())
    monkeypatch.setattr(run_rag.psycopg, "connect", MagicMock())
    monkeypatch.setattr(run_rag, "search_kb", Mock(return_value=[PASSAGE]))
    monkeypatch.setattr(run_rag, "draft_from_evidence", Mock(
        return_value=RagResult(reason="provider_error_503")
    ))
    report, passed = run_rag.run()
    assert passed is False
    assert json.loads(report.read_text())["passed"] == 0
