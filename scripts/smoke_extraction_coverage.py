"""Dependency-free smoke validation for privacy-safe extraction coverage."""

from falcon_intel.extraction_coverage import (
    build_extraction_coverage_report,
    render_extraction_coverage_markdown,
)


def main() -> int:
    intake = {
        "files": [
            {"file_id": "synthetic-final", "candidate_role": "final_report", "extension": ".pdf"},
            {"file_id": "synthetic-support", "candidate_role": "source_document", "extension": ".xlsx"},
        ]
    }
    knowledge_report = {
        "report_candidates": [
            {
                "file_id": "synthetic-final",
                "file_name": "Synthetic Final Report.pdf",
                "fields": {
                    "property_address": (
                        {
                            "value": "100 Sample Street",
                            "confidence": "high",
                            "extraction_method": "deterministic label match",
                            "source_hint": "page 1",
                        },
                    )
                },
                "warnings": (),
            }
        ],
        "warnings": ("no embedded/searchable PDF text found; OCR was not attempted",),
        "errors": (),
    }
    verification_report = {
        "report_facts": [
            {
                "file_id": "synthetic-final",
                "file_name": "Synthetic Final Report.pdf",
                "facts": (
                    {
                        "field_name": "property_address",
                        "verified_value": "100 Sample Street",
                        "verification_status": "probable",
                        "confidence": "medium",
                        "supporting_evidence": (
                            {
                                "field_name": "property_address",
                                "value": "100 Sample Street",
                                "normalized_value": "100 sample street",
                                "source_type": "extracted_metadata",
                                "source_label": "page 1",
                                "source_reference": "synthetic-final:property_address:1",
                                "confidence": "high",
                                "method": "synthetic deterministic label",
                            },
                        ),
                        "conflicting_evidence": (),
                    },
                    {
                        "field_name": "income_approach",
                        "verified_value": None,
                        "verification_status": "missing",
                        "confidence": "missing",
                        "supporting_evidence": (),
                        "conflicting_evidence": (),
                    },
                ),
                "warnings": (),
            }
        ],
        "warnings": (),
        "errors": (),
    }

    report = build_extraction_coverage_report(
        intake=intake,
        knowledge_report=knowledge_report,
        verification_report=verification_report,
        generated_at="2026-07-07T00:00:00+00:00",
    )
    markdown = render_extraction_coverage_markdown(report)

    assert report.source_file_count == 2
    assert report.candidate_final_report_count == 1
    assert report.warning_type_counts["no_searchable_text"] == 1
    assert report.promotion_field_summary["needs_review"]["count"] == 1
    assert report.promotion_field_summary["missing"]["count"] == 1
    assert "100 Sample Street" not in markdown
    assert "address-like" in markdown
    print("extraction coverage smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
