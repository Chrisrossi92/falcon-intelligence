from pathlib import Path

from falcon_intel.verification_engine import (
    VerificationReport,
    build_verification_summary,
    normalize_fact_value,
    render_verification_summary,
    run_verification,
    save_verification_outputs,
    verify_report_candidate,
)


def _candidate(**field_overrides: object) -> dict[str, object]:
    fields: dict[str, object] = {
        "report_title": [
            {
                "value": "Restricted Appraisal Report",
                "confidence": "medium",
                "extraction_method": "deterministic title phrase",
                "source_hint": "page 1",
            }
        ],
        "client": [
            {
                "value": "Example Bank",
                "confidence": "high",
                "extraction_method": "deterministic label match",
                "source_hint": "page 1",
            }
        ],
    }
    fields.update(field_overrides)
    return {
        "file_id": "synthetic-final",
        "file_name": "Restricted Appraisal Report.pdf",
        "file_path": "synthetic/Restricted Appraisal Report.pdf",
        "fields": fields,
        "approaches_referenced": {
            "income_approach": {
                "value": "present",
                "confidence": "medium",
                "extraction_method": "deterministic phrase presence",
                "source_hint": "page 2",
            }
        },
        "sections_detected": {},
        "warnings": [],
    }


def _facts_by_name(candidate: dict[str, object]) -> dict[str, object]:
    report = verify_report_candidate(candidate, timestamp="2026-06-30T00:00:00+00:00")
    return {fact.field_name: fact for fact in report.facts}


def test_agreement_verifies_fact_with_high_confidence() -> None:
    facts = _facts_by_name(_candidate())

    report_type = facts["report_type"]

    assert report_type.verification_status == "verified"
    assert report_type.confidence == "high"
    assert report_type.verified_value == "restricted appraisal report"
    assert report_type.verification_method == "agreement rule"
    assert len(report_type.supporting_evidence) >= 2


def test_conflicting_values_do_not_guess() -> None:
    facts = _facts_by_name(
        _candidate(
            client=[
                {
                    "value": "Example Bank",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 1",
                },
                {
                    "value": "Example Credit Union",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 2",
                },
            ]
        )
    )

    client = facts["client"]

    assert client.verification_status == "conflicting"
    assert client.verified_value is None
    assert len(client.conflicting_evidence) == 2
    assert client.diagnostics["field_name"] == "client"
    assert client.diagnostics["candidate_count"] == 2
    assert client.diagnostics["status_reason"] == "conflicting_normalized_values"
    assert len(client.diagnostics["normalized_candidate_fingerprints"]) == 2
    assert "Example Bank" not in str(client.diagnostics)


def test_missing_values_remain_missing() -> None:
    facts = _facts_by_name(_candidate())

    report_date = facts["report_date"]

    assert report_date.verification_status == "missing"
    assert report_date.verified_value is None
    assert report_date.verification_method == "missing rule"


def test_normalization_matches_common_address_differences() -> None:
    assert normalize_fact_value("property_address", "100 Sample St.") == normalize_fact_value(
        "property_address", "100 SAMPLE STREET"
    )


def test_same_normalized_value_with_formatting_differences_does_not_conflict() -> None:
    facts = _facts_by_name(
        _candidate(
            property_address=[
                {
                    "value": "100 Sample St.",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 1",
                },
                {
                    "value": "100 SAMPLE STREET",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 2",
                },
            ]
        )
    )

    property_address = facts["property_address"]

    assert property_address.verification_status == "verified"
    assert property_address.confidence == "high"
    assert property_address.verified_value == "100 Sample St."


def test_single_source_candidate_is_probable() -> None:
    facts = _facts_by_name(_candidate())

    client = facts["client"]

    assert client.verification_status == "probable"
    assert client.confidence == "medium"


def test_verification_ledger_contains_evidence_and_timestamp() -> None:
    facts = _facts_by_name(_candidate())

    report_type = facts["report_type"]

    assert report_type.verification_timestamp == "2026-06-30T00:00:00+00:00"
    assert report_type.source_references
    assert report_type.notes


def test_summary_generation_and_outputs(tmp_path: Path) -> None:
    report_facts = verify_report_candidate(_candidate(), timestamp="2026-06-30T00:00:00+00:00")
    report = VerificationReport(
        verification_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_knowledge_path="synthetic-knowledge.json",
        report_facts=(report_facts,),
    )

    summary = build_verification_summary(report)
    outputs = save_verification_outputs(report, tmp_path)

    assert summary["verified_facts"] >= 1
    assert Path(outputs["json"]).exists()
    assert Path(outputs["markdown"]).name == "verification-summary.md"
    assert "deterministic verified-fact ledgers only" in render_verification_summary(report)


def test_runner_consumes_historical_knowledge_output(tmp_path: Path) -> None:
    knowledge_path = tmp_path / "historical-knowledge-report.json"
    knowledge_path.write_text(
        """
        {
          "report_candidates": [
            {
              "file_id": "synthetic-final",
              "file_name": "Restricted Appraisal Report.pdf",
              "file_path": "synthetic/Restricted Appraisal Report.pdf",
              "fields": {
                "report_title": [
                  {
                    "value": "Restricted Appraisal Report",
                    "confidence": "medium",
                    "extraction_method": "deterministic title phrase",
                    "source_hint": "page 1"
                  }
                ]
              },
              "approaches_referenced": {},
              "sections_detected": {},
              "warnings": []
            }
          ],
          "warnings": [],
          "errors": []
        }
        """,
        encoding="utf-8",
    )

    report = run_verification(knowledge_path)

    assert report.report_facts[0].file_id == "synthetic-final"
    assert any(fact.verification_status == "verified" for fact in report.report_facts[0].facts)
