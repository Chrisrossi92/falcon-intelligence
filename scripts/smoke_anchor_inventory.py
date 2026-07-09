"""Smoke validation for privacy-safe anchor-family inventory."""

from falcon_intel.anchor_inventory import (
    AnchorInventoryReport,
    PageText,
    build_anchor_inventory_rows,
    render_anchor_inventory_markdown,
)


def main() -> int:
    raw_private_text = """
    Restricted Appraisal Report
    Client: Example Bank
    Intended User: Example Bank
    The property was inspected during a site visit.
    Certification of Appraisal
    Alex Example
    Certified General Real Estate Appraiser
    Review Certification
    Reviewed By Riley Example
    Sales Comparison Approach
    Income Approach
    Cost Approach
    """
    rows = build_anchor_inventory_rows(
        1,
        (PageText(page_number=1, text=raw_private_text),),
        source_tier="final_report_pdf",
        source_type="pdf",
    )
    report = AnchorInventoryReport(
        inventory_version="1",
        generated_at="2026-07-07T00:00:00+00:00",
        source_intake_path="synthetic-intake.json",
        analyzed_report_count=1,
        inventory_rows=rows,
        aggregate_counts={
            "anchor_family": {},
            "source_tier": {},
            "source_type": {},
            "page_bucket": {},
            "report_index": {},
        },
    )
    markdown = render_anchor_inventory_markdown(report)

    families = {row.anchor_family for row in rows}
    assert "inspection_site_visit" in families
    assert "appraiser_signature_certification" in families
    assert "reviewer_review" in families
    assert "report_title_title_block" in families
    assert "client_intended_user" in families
    assert "approach_sections" in families
    assert "Example Bank" not in markdown
    assert "Alex Example" not in markdown
    assert "Riley Example" not in markdown
    assert "Restricted Appraisal Report" not in markdown
    assert "family=inspection_site_visit" in markdown
    print("anchor inventory smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
