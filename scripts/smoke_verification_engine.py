"""Smoke check for the local deterministic verification engine."""

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.verification_engine import (
    build_verification_summary,
    save_verification_outputs,
    verify_report_candidate,
    VerificationReport,
)


def main() -> int:
    candidate = {
        "file_id": "synthetic-final",
        "file_name": "Restricted Appraisal Report.pdf",
        "file_path": "synthetic/Restricted Appraisal Report.pdf",
        "fields": {
            "report_title": [
                {
                    "value": "Restricted Appraisal Report",
                    "confidence": "medium",
                    "extraction_method": "deterministic title phrase",
                    "source_hint": "page 1",
                }
            ],
            "property_address": [
                {
                    "value": "100 Sample St.",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 1",
                },
                {
                    "value": "100 Sample Street",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 2",
                },
            ],
            "client": [
                {
                    "value": "Example Bank",
                    "confidence": "high",
                    "extraction_method": "deterministic label match",
                    "source_hint": "page 1",
                }
            ],
        },
        "approaches_referenced": {},
        "sections_detected": {},
        "warnings": (),
    }
    report_facts = verify_report_candidate(candidate, timestamp="2026-06-30T00:00:00+00:00")
    facts_by_name = {fact.field_name: fact for fact in report_facts.facts}
    assert facts_by_name["report_type"].verification_status == "verified"
    assert facts_by_name["property_address"].verification_status == "verified"
    assert facts_by_name["property_address"].confidence == "high"
    assert facts_by_name["report_date"].verification_status == "missing"
    assert facts_by_name["property_address"].diagnostics["status_reason"] == "independent_agreement"
    assert facts_by_name["report_date"].diagnostics["status_reason"] == "missing_candidate"

    conflicting = verify_report_candidate(
        {
            **candidate,
            "fields": {
                **candidate["fields"],
                "client": [
                    {"value": "Example Bank", "confidence": "high", "source_hint": "page 1"},
                    {"value": "Example Credit Union", "confidence": "high", "source_hint": "page 2"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    conflict_fact = {fact.field_name: fact for fact in conflicting.facts}["client"]
    assert conflict_fact.verification_status == "conflicting"
    assert conflict_fact.verified_value is None
    assert conflict_fact.diagnostics["field_name"] == "client"
    assert conflict_fact.diagnostics["candidate_count"] == 2
    assert len(conflict_fact.diagnostics["normalized_candidate_fingerprints"]) == 2
    assert "Example Bank" not in str(conflict_fact.diagnostics)

    low_confidence = verify_report_candidate(
        {
            **candidate,
            "fields": {
                **candidate["fields"],
                "inspection_date": [{"value": "June 2, 2026", "confidence": "low", "source_hint": "page 1"}],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    review_fact = {fact.field_name: fact for fact in low_confidence.facts}["inspection_date"]
    assert review_fact.verification_status == "needs_review"
    assert review_fact.confidence == "low"

    final_docx_agreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "client": [
                    {"value": "Example Bank", "confidence": "high", "source_hint": "page 1"},
                    {"value": "Example Bank", "confidence": "high", "source_hint": "docx final report: synthetic-docx"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    client_fact = {fact.field_name: fact for fact in final_docx_agreement.facts}["client"]
    assert client_fact.verification_status == "verified"
    assert set(client_fact.diagnostics["provenance_tiers"]) == {"final_report_docx", "final_report_pdf"}

    companion_agreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "property_address": [
                    {"value": "100 Sample St.", "confidence": "high", "source_hint": "page 1"},
                    {"value": "100 Sample Street", "confidence": "high", "source_hint": "docx companion source: synthetic-docx"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    address_fact = {fact.field_name: fact for fact in companion_agreement.facts}["property_address"]
    assert address_fact.verification_status == "verified"

    companion_disagreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "intended_use": [
                    {"value": "Loan underwriting", "confidence": "high", "source_hint": "page 9"},
                    {"value": "Portfolio review", "confidence": "high", "source_hint": "docx companion source: synthetic-docx"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    intended_use_fact = {fact.field_name: fact for fact in companion_disagreement.facts}["intended_use"]
    assert intended_use_fact.verification_status == "needs_review"
    assert intended_use_fact.diagnostics["status_reason"] == "lower_tier_evidence_disagrees_with_final_report"
    assert intended_use_fact.diagnostics["provenance_tier_counts"]["final_report_pdf"] == 1
    assert intended_use_fact.diagnostics["provenance_tier_counts"]["same_order_docx_companion"] == 1

    intended_use_boilerplate_agreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "intended_use": [
                    {
                        "value": "The intended use of this appraisal is to assist the client with loan underwriting.",
                        "confidence": "high",
                        "source_hint": "page 3",
                    },
                    {
                        "value": "For lending and collateral financing purposes",
                        "confidence": "high",
                        "source_hint": "docx final report: synthetic-docx",
                    },
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    intended_use_agreement = {fact.field_name: fact for fact in intended_use_boilerplate_agreement.facts}["intended_use"]
    assert intended_use_agreement.verification_status == "verified"

    property_type_variant_agreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "property_type": [
                    {"value": "Industrial building", "confidence": "high", "source_hint": "page 1"},
                    {"value": "Industrial", "confidence": "high", "source_hint": "docx final report: synthetic-docx"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    property_type_variant = {fact.field_name: fact for fact in property_type_variant_agreement.facts}["property_type"]
    assert property_type_variant.verification_status == "verified"

    property_type_authoritative_conflict = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "property_type": [
                    {"value": "Industrial", "confidence": "high", "source_hint": "page 1"},
                    {"value": "Retail", "confidence": "high", "source_hint": "docx final report: synthetic-docx"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    property_type_conflict = {fact.field_name: fact for fact in property_type_authoritative_conflict.facts}["property_type"]
    assert property_type_conflict.verification_status == "conflicting"
    assert property_type_conflict.diagnostics["status_reason"] == "conflicting_normalized_values"

    date_format_agreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "report_date": [
                    {"value": "June 15, 2026", "confidence": "high", "source_hint": "page 1"},
                    {"value": "06/15/2026", "confidence": "high", "source_hint": "docx final report: synthetic-docx"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    report_date_fact = {fact.field_name: fact for fact in date_format_agreement.facts}["report_date"]
    assert report_date_fact.verification_status == "verified"

    date_lower_tier_disagreement = verify_report_candidate(
        {
            **candidate,
            "fields": {
                "report_date": [
                    {"value": "June 15, 2026", "confidence": "high", "source_hint": "page 1"},
                    {"value": "2026-07-01", "confidence": "medium", "source_hint": "intake filename/folder metadata"},
                ],
            },
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    lower_tier_report_date = {fact.field_name: fact for fact in date_lower_tier_disagreement.facts}["report_date"]
    assert lower_tier_report_date.verification_status == "needs_review"
    assert lower_tier_report_date.diagnostics["status_reason"] == "lower_tier_evidence_disagrees_with_final_report"

    with TemporaryDirectory() as temp_dir:
        report = VerificationReport(
            verification_version="1",
            generated_at="2026-06-30T00:00:00+00:00",
            source_knowledge_path="synthetic-knowledge.json",
            report_facts=(report_facts,),
        )
        summary = build_verification_summary(report)
        assert summary["verified_facts"] >= 1
        outputs = save_verification_outputs(report, Path(temp_dir))
        assert Path(outputs["json"]).exists()
        assert Path(outputs["markdown"]).exists()

    print("verification engine smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
