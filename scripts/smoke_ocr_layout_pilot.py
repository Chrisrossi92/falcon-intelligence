"""Smoke validation for privacy-safe OCR/layout pilot diagnostics."""

from falcon_intel.ocr_layout_pilot import (
    OCRLayoutPilotReport,
    build_ocr_layout_pilot_report,
    build_synthetic_ocr_diagnostics,
    render_ocr_layout_pilot_markdown,
)


def main() -> int:
    private_date = "July 2, 2026"
    private_reviewer = "Riley Example"
    inspection_text = f"""
    Site Visit
    The subject was inspected on {private_date}.
    """
    reviewer_text = f"""
    Review Certification
    Reviewed By: {private_reviewer}
    Review Appraiser
    """

    diagnostics = (
        *build_synthetic_ocr_diagnostics(
            report_index=1,
            page_bucket="first_page",
            target_field="inspection_date",
            ocr_text=inspection_text,
        ),
        *build_synthetic_ocr_diagnostics(
            report_index=1,
            page_bucket="late_pages",
            target_field="reviewer_name",
            ocr_text=reviewer_text,
        ),
    )
    report = OCRLayoutPilotReport(
        pilot_version="1",
        generated_at="2026-07-08T00:00:00+00:00",
        source_intake_path="synthetic-intake.json",
        ocr_enabled=True,
        candidate_final_report_count=1,
        analyzed_report_count=1,
        target_fields=("inspection_date", "reviewer_name"),
        diagnostics=diagnostics,
        aggregate_counts={
            "target_field": {"inspection_date": 1, "reviewer_name": 1},
            "page_bucket": {"first_page": 1, "late_pages": 1},
            "anchor_family_detected": {"true": 2},
            "candidate_shape": {"date-like": 1, "person-like": 1},
            "length_bucket": {"13-32": 2},
            "ocr_status": {"available": 2},
            "warning_status": {"none": 2},
        },
    )
    markdown = render_ocr_layout_pilot_markdown(report)

    assert report.diagnostics[0].candidate_shape == "date-like"
    assert report.diagnostics[1].candidate_shape == "person-like"
    assert report.diagnostics[0].fingerprint
    assert report.diagnostics[1].fingerprint
    assert private_date not in markdown
    assert private_reviewer not in markdown
    assert "subject was inspected" not in markdown.lower()
    assert "Review Certification" not in markdown
    assert "shape=date-like" in markdown
    assert "shape=person-like" in markdown
    assert "fingerprint=" in markdown

    intake = {
        "files": [
            {
                "file_id": "synthetic-final",
                "candidate_role": "final_report",
                "extension": ".pdf",
                "file_path": r"C:\private\Example Client\final.pdf",
            }
        ]
    }
    feasibility_report = {
        "candidate_final_report_count": 1,
        "rows": (
            {
                "report_index": 1,
                "field_recommendations": {
                    "inspection_date": {
                        "ocr_recommended": True,
                        "recommended_page_buckets": ("first_page", "early_pages"),
                    },
                    "reviewer_name": {
                        "ocr_recommended": True,
                        "recommended_page_buckets": ("late_pages", "document"),
                    },
                },
            },
        ),
    }
    availability_report = build_ocr_layout_pilot_report(
        intake=intake,
        feasibility_report=feasibility_report,
        source_intake_path="synthetic-intake.json",
        enable_ocr=False,
        generated_at="2026-07-08T00:00:00+00:00",
    )
    availability_markdown = render_ocr_layout_pilot_markdown(availability_report)
    assert availability_report.aggregate_counts["ocr_status"]["opt_in_required"] == 4
    assert "Example Client" not in availability_markdown
    assert "final.pdf" not in availability_markdown
    print("ocr layout pilot smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
