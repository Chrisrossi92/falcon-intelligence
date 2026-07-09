"""Smoke validation for privacy-safe OCR/layout feasibility planning."""

from falcon_intel.ocr_feasibility import (
    build_ocr_feasibility_report,
    render_ocr_feasibility_markdown,
)


def main() -> int:
    private_path = r"C:\private\Example Client\final-report.pdf"
    private_title = "Private Example Appraisal Report"
    private_appraiser = "Alex Example, MAI"
    private_date = "July 1, 2026"

    intake = {
        "files": [
            {
                "file_id": "synthetic-final",
                "candidate_role": "final_report",
                "extension": ".pdf",
                "file_path": private_path,
            },
        ],
        "candidate_order_groups": (),
    }
    knowledge_report = {
        "report_candidates": [
            {
                "file_id": "synthetic-final",
                "file_path": private_path,
                "file_name": "private-final-report.pdf",
                "extraction_status": "extracted",
                "fields": {
                    "report_title": (
                        {
                            "value": private_title,
                            "confidence": "medium",
                            "source_hint": "page 1",
                        },
                    ),
                    "appraiser_name": (
                        {
                            "value": private_appraiser,
                            "confidence": "high",
                            "source_hint": "page 28",
                        },
                    ),
                    "inspection_date": (
                        {
                            "value": private_date,
                            "confidence": "missing",
                            "source_hint": None,
                        },
                    ),
                },
            }
        ],
        "warnings": (),
    }
    verification_report = {
        "report_facts": [
            {
                "file_id": "synthetic-final",
                "facts": (
                    {
                        "field_name": "report_title",
                        "verification_status": "probable",
                        "supporting_evidence": (
                            {
                                "source_type": "final_report_pdf",
                                "source_label": "page 1",
                                "value": private_title,
                            },
                        ),
                    },
                    {
                        "field_name": "appraiser_name",
                        "verification_status": "verified",
                        "supporting_evidence": (
                            {
                                "source_type": "final_report_pdf",
                                "source_label": "page 28",
                                "value": private_appraiser,
                            },
                        ),
                    },
                    {
                        "field_name": "inspection_date",
                        "verification_status": "missing",
                        "supporting_evidence": (),
                        "conflicting_evidence": (),
                    },
                    {
                        "field_name": "reviewer_name",
                        "verification_status": "missing",
                        "supporting_evidence": (),
                        "conflicting_evidence": (),
                    },
                ),
            }
        ],
    }
    anchor_inventory_report = {
        "inventory_rows": (
            {
                "report_index": 1,
                "source_tier": "final_report_pdf",
                "source_type": "pdf",
                "page_bucket": "late_pages",
                "anchor_family": "appraiser_signature_certification",
                "count": 2,
            },
            {
                "report_index": 1,
                "source_tier": "final_report_pdf",
                "source_type": "pdf",
                "page_bucket": "first_page",
                "anchor_family": "report_title_title_block",
                "count": 1,
            },
        ),
        "warnings": (),
    }

    report = build_ocr_feasibility_report(
        intake=intake,
        knowledge_report=knowledge_report,
        verification_report=verification_report,
        anchor_inventory_report=anchor_inventory_report,
        source_intake_path="synthetic-intake.json",
        generated_at="2026-07-08T00:00:00+00:00",
    )
    markdown = render_ocr_feasibility_markdown(report)

    assert report.analyzed_report_count == 1
    assert report.field_recommendations["inspection_date"]["ocr_recommended"] is True
    assert report.field_recommendations["reviewer_name"]["ocr_recommended"] is True
    assert report.field_recommendations["appraiser_name"]["ocr_recommended"] is False
    assert "target_field_missing_and_anchor_absent_from_searchable_text" in markdown
    assert "field=inspection_date" in markdown
    assert private_path not in markdown
    assert private_title not in markdown
    assert private_appraiser not in markdown
    assert private_date not in markdown
    assert "Example Client" not in markdown
    print("ocr feasibility smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
