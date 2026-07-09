"""Smoke validation for privacy-safe appraiser/title anchor-to-field diagnostics."""

from falcon_intel.anchor_inventory import (
    AnchorToFieldDiagnosticsReport,
    PageText,
    build_anchor_to_field_diagnostics,
    render_anchor_to_field_diagnostics_markdown,
)


def main() -> int:
    pages = (
        PageText(page_number=1, text="Certified General Real Estate Appraiser"),
        PageText(
            page_number=2,
            text="""
            Certification of Appraisal
            Value Services LLC
            Certified General Real Estate Appraiser
            """,
        ),
        PageText(
            page_number=3,
            text="""
            Certification of Appraisal
            Appraiser Independence Statement
            Certified General Real Estate Appraiser
            """,
        ),
        PageText(
            page_number=4,
            text="""
            Certification of Appraisal
            This synthetic line is intentionally long enough to fail the candidate length bucket before person validation.
            Certified General Real Estate Appraiser
            """,
        ),
        PageText(page_number=5, text="Appraisal Report"),
        PageText(
            page_number=6,
            text="""
            Market Value
            Appraisal Report
            """,
        ),
    )
    diagnostics = build_anchor_to_field_diagnostics(
        1,
        pages,
        source_tier="final_report_pdf",
        source_type="pdf",
    )
    report = AnchorToFieldDiagnosticsReport(
        diagnostics_version="1",
        generated_at="2026-07-07T00:00:00+00:00",
        source_intake_path="synthetic-intake.json",
        analyzed_report_count=1,
        diagnostic_count=len(diagnostics),
        diagnostics=diagnostics,
        aggregate_counts={
            "field_name": {},
            "rejection_reason": {},
            "anchor_family": {},
            "source_tier": {},
            "source_type": {},
            "page_bucket": {},
            "candidate_shape": {},
            "candidate_length_bucket": {},
            "provenance_method": {},
        },
    )
    markdown = render_anchor_to_field_diagnostics_markdown(report)
    reasons = {item.rejection_reason for item in diagnostics}

    assert "no_nearby_candidate" in reasons
    assert "company_or_title_not_person" in reasons
    assert "failed_person_name_validation" in reasons
    assert "candidate_too_long" in reasons
    assert "title_candidate_too_generic" in reasons
    assert "accepted_candidate_shape" in reasons
    assert "Value Services LLC" not in markdown
    assert "Appraiser Independence Statement" not in markdown
    assert "Market Value Appraisal Report" not in markdown
    assert "reason=title_candidate_too_generic" in markdown
    print("anchor-to-field diagnostics smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
