"""Smoke validation for privacy-safe unresolved-field diagnostics."""

from falcon_intel.extraction_diagnostics import (
    build_extraction_diagnostics_report,
    render_extraction_diagnostics_markdown,
)


def main() -> int:
    intake = {
        "files": [
            {"file_id": "synthetic-final", "candidate_role": "final_report", "extension": ".pdf"},
        ]
    }
    knowledge_report = {
        "report_candidates": [
            {
                "file_id": "synthetic-final",
                "fields": {
                    "inspection_date": (
                        {
                            "value": None,
                            "confidence": "missing",
                            "extraction_method": "deterministic pattern matching",
                            "warning": "inspection date not found",
                        },
                    ),
                },
                "warnings": (),
            }
        ],
        "warnings": (),
        "errors": (),
    }
    verification_report = {
        "report_facts": [
            {
                "file_id": "synthetic-final",
                "facts": (
                    {
                        "field_name": "inspection_date",
                        "verified_value": None,
                        "verification_status": "missing",
                        "confidence": "missing",
                        "supporting_evidence": (),
                        "conflicting_evidence": (),
                        "diagnostics": {"status_reason": "missing_candidate"},
                    },
                    {
                        "field_name": "appraiser_name",
                        "verified_value": None,
                        "verification_status": "conflicting",
                        "confidence": "conflicting",
                        "supporting_evidence": (),
                        "conflicting_evidence": (
                            {
                                "field_name": "appraiser_name",
                                "value": "Alex Example",
                                "normalized_value": "alex example",
                                "source_type": "final_report_pdf",
                                "source_label": "page 12",
                                "source_reference": "synthetic-final:appraiser_name:1",
                                "confidence": "high",
                                "method": "signature block: appraiser credential anchor",
                            },
                            {
                                "field_name": "appraiser_name",
                                "value": "Riley Example",
                                "normalized_value": "riley example",
                                "source_type": "same_order_docx_companion",
                                "source_label": "docx companion source: synthetic-docx",
                                "source_reference": "synthetic-final:appraiser_name:2",
                                "confidence": "high",
                                "method": "deterministic label match: Appraiser",
                            },
                        ),
                        "diagnostics": {"status_reason": "conflicting_normalized_values"},
                    },
                ),
                "warnings": (),
            }
        ],
        "warnings": (),
        "errors": (),
    }

    report = build_extraction_diagnostics_report(
        intake=intake,
        knowledge_report=knowledge_report,
        verification_report=verification_report,
        source_intake_path="synthetic-intake.json",
        generated_at="2026-07-07T00:00:00+00:00",
    )
    markdown = render_extraction_diagnostics_markdown(report)

    assert report.unresolved_count == 3
    assert report.aggregate_categories["candidate_shapes"]["person-like"] == 2
    assert report.aggregate_categories["candidate_shapes"]["missing"] == 1
    assert report.aggregate_categories["source_tiers"]["same_order_docx_companion"] == 1
    assert "Alex Example" not in markdown
    assert "Riley Example" not in markdown
    assert "synthetic-docx" not in markdown
    assert "person-like" in markdown
    assert "fingerprint=" in markdown
    print("extraction diagnostics smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
