from falcon_intel.extraction_coverage import (
    build_extraction_coverage_report,
    render_extraction_coverage_markdown,
)
from falcon_intel.historical_knowledge import PYPDF_MISSING_WARNING


def _synthetic_intake() -> dict[str, object]:
    return {
        "files": [
            {"file_id": "file-a", "candidate_role": "final_report", "extension": ".pdf"},
            {"file_id": "file-b", "candidate_role": "source_document", "extension": ".xlsx"},
        ]
    }


def _synthetic_knowledge_report() -> dict[str, object]:
    return {
        "report_candidates": [
            {
                "file_id": "file-a",
                "file_name": "Synthetic Final Report.pdf",
                "fields": {
                    "client": (
                        {
                            "value": "Example Bank",
                            "confidence": "high",
                            "extraction_method": "deterministic label match",
                            "source_hint": "page 1",
                        },
                    ),
                    "property_address": (
                        {
                            "value": "100 Sample Street",
                            "confidence": "high",
                            "extraction_method": "deterministic label match",
                            "source_hint": "page 1",
                        },
                    ),
                },
                "warnings": ("client not found",),
            }
        ],
        "warnings": (PYPDF_MISSING_WARNING,),
        "errors": (),
    }


def _fact(field_name: str, value: str | None, status: str, confidence: str) -> dict[str, object]:
    evidence = []
    if value:
        evidence.append(
            {
                "field_name": field_name,
                "value": value,
                "normalized_value": value.lower(),
                "source_type": "extracted_metadata",
                "source_label": "page 1",
                "source_reference": f"file-a:{field_name}:1",
                "confidence": confidence,
                "method": "synthetic deterministic label",
            }
        )
    return {
        "field_name": field_name,
        "verified_value": value,
        "verification_status": status,
        "confidence": confidence,
        "supporting_evidence": tuple(evidence),
        "conflicting_evidence": (),
        "verification_method": "synthetic rule",
        "verification_timestamp": "2026-07-07T00:00:00+00:00",
        "notes": (),
        "source_references": tuple(item["source_reference"] for item in evidence),
    }


def _synthetic_verification_report() -> dict[str, object]:
    return {
        "report_facts": [
            {
                "file_id": "file-a",
                "file_name": "Synthetic Final Report.pdf",
                "facts": (
                    _fact("property_address", "100 Sample Street", "probable", "medium"),
                    _fact("client", "Example Bank", "probable", "medium"),
                    _fact("effective_date", None, "missing", "missing"),
                    {
                        "field_name": "intended_user",
                        "verified_value": None,
                        "verification_status": "conflicting",
                        "confidence": "conflicting",
                        "supporting_evidence": (),
                        "conflicting_evidence": (
                            {"source_label": "page 1", "source_reference": "file-a:intended_user:1"},
                            {"source_label": "page 2", "source_reference": "file-a:intended_user:2"},
                        ),
                        "verification_method": "conflict rule",
                        "verification_timestamp": "2026-07-07T00:00:00+00:00",
                        "notes": (),
                        "source_references": ("file-a:intended_user:1", "file-a:intended_user:2"),
                        "diagnostics": {
                            "status_reason": "conflicting_normalized_values",
                            "field_name": "intended_user",
                            "candidate_count": 2,
                            "normalized_candidate_fingerprints": ("abc1230000", "def4560000"),
                            "source_labels": ("page 1", "page 2"),
                        },
                    },
                    _fact("sales_comparison_approach", "present", "probable", "medium"),
                    _fact("income_approach", None, "missing", "missing"),
                    _fact("cost_approach", None, "missing", "missing"),
                ),
                "warnings": (),
            }
        ],
        "warnings": (),
        "errors": (),
    }


def _synthetic_knowledge_objects_report() -> dict[str, object]:
    return {
        "reports": [
            {
                "file_id": "file-a",
                "object_candidates": [
                    {
                        "object_type": "property",
                        "readiness": "needs_review",
                        "missing_required_fields": (),
                        "review_required_fields": ("property_address",),
                        "conflicting_fields": (),
                    },
                    {
                        "object_type": "client_user",
                        "readiness": "blocked",
                        "missing_required_fields": ("intended_user",),
                        "review_required_fields": ("client",),
                        "conflicting_fields": ("intended_user",),
                    },
                ],
            }
        ]
    }


def test_builds_privacy_safe_coverage_counts() -> None:
    report = build_extraction_coverage_report(
        intake=_synthetic_intake(),
        knowledge_report=_synthetic_knowledge_report(),
        verification_report=_synthetic_verification_report(),
        knowledge_objects_summary={"readiness_breakdown": {"needs_review": 1}},
        knowledge_objects_report=_synthetic_knowledge_objects_report(),
        memory_graph_summary={"graph_readiness_breakdown": {"needs_review": 1}},
        source_intake_path="synthetic-intake.json",
        generated_at="2026-07-07T00:00:00+00:00",
    )

    assert report.source_file_count == 2
    assert report.candidate_final_report_count == 1
    assert report.analyzed_report_count == 1
    assert report.field_coverage["effective_date"]["missing"] == 1
    assert report.approach_indicators["sales_comparison_approach"]["present"] == 1
    assert report.approach_indicators["income_approach"]["missing"] == 1
    assert report.warning_type_counts["pdf_text_library_missing"] == 1
    assert report.conflict_fields_by_type[0]["field_name"] == "intended_user"
    assert report.conflict_fields_by_type[0]["normalized_candidate_fingerprints"] == ("abc1230000", "def4560000")
    assert report.conflict_fields_by_type[0]["source_labels"] == ("page 1", "page 2")
    assert report.promotion_field_summary["needs_review"]["count"] == 3
    assert report.promotion_field_summary["blocked"]["count"] == 1
    assert report.readiness_reason_counts["blocked_by_conflict"] == 1
    assert report.promotion_blockers[0]["readiness"] == "blocked"
    assert "effective_date" in {item["field_name"] for item in report.common_missing_fields}


def test_rendered_report_redacts_private_values() -> None:
    report = build_extraction_coverage_report(
        intake=_synthetic_intake(),
        knowledge_report=_synthetic_knowledge_report(),
        verification_report=_synthetic_verification_report(),
        knowledge_objects_report=_synthetic_knowledge_objects_report(),
        source_intake_path="synthetic-intake.json",
        generated_at="2026-07-07T00:00:00+00:00",
    )

    markdown = render_extraction_coverage_markdown(report)

    assert "100 Sample Street" not in markdown
    assert "Example Bank" not in markdown
    assert "field=property_address" in markdown
    assert "type=address-like" in markdown
    assert "fingerprint=" in markdown
    assert "abc1230000" in markdown
