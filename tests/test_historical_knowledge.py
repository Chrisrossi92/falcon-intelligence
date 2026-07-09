from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

from falcon_intel.historical_knowledge import (
    HistoricalKnowledgeReport,
    PYPDF_MISSING_WARNING,
    PYTHON_DOCX_MISSING_WARNING,
    PageText,
    _extract_embedded_docx_text,
    _extract_embedded_pdf_text,
    extract_report_metadata_from_pages,
    run_historical_knowledge_extraction,
    render_historical_knowledge_summary,
    save_historical_knowledge_outputs,
)


def _synthetic_pages() -> tuple[PageText, ...]:
    return (
        PageText(
            page_number=1,
            text="""
            Restricted Appraisal Report
            Property Address: 100 Sample Street
            Property Type: Industrial warehouse
            Client: Example Bank
            Intended User: Example Bank
            Intended Use: Loan underwriting
            Effective Date: June 1, 2026
            Report Date: June 15, 2026
            Date of Inspection: May 30, 2026
            Appraiser: Alex Example
            Reviewer: Riley Example
            """,
        ),
        PageText(
            page_number=2,
            text="""
            The appraiser considered the Sales Comparison Approach.
            The Income Approach was also considered.
            The Cost Approach was not developed.

            Extraordinary Assumptions
            Hypothetical Conditions
            Certification
            General Assumptions and Limiting Conditions
            """,
        ),
    )


def test_extracts_effective_report_and_inspection_dates() -> None:
    candidate = extract_report_metadata_from_pages(_synthetic_pages())

    assert candidate.fields["effective_date"][0].value == "June 1, 2026"
    assert candidate.fields["report_date"][0].value == "June 15, 2026"
    assert candidate.fields["inspection_date"][0].value == "May 30, 2026"


def test_extracts_client_intended_user_and_intended_use() -> None:
    candidate = extract_report_metadata_from_pages(_synthetic_pages())

    assert candidate.fields["client"][0].value == "Example Bank"
    assert candidate.fields["intended_user"][0].value == "Example Bank"
    assert candidate.fields["intended_use"][0].value == "Loan underwriting"


def test_extracts_report_type_and_basic_people_fields() -> None:
    candidate = extract_report_metadata_from_pages(_synthetic_pages())

    assert candidate.fields["report_type"][0].value == "restricted appraisal report"
    assert candidate.fields["property_type"][0].value == "Industrial warehouse"
    assert candidate.fields["appraiser_name"][0].value == "Alex Example"
    assert candidate.fields["reviewer_name"][0].value == "Riley Example"


def test_detects_approaches_and_sections() -> None:
    candidate = extract_report_metadata_from_pages(_synthetic_pages())

    assert candidate.approaches_referenced["sales_comparison_approach"].value == "present"
    assert candidate.approaches_referenced["income_approach"].value == "present"
    assert candidate.approaches_referenced["cost_approach"].value == "present"
    assert candidate.sections_detected["extraordinary_assumptions_present"].value == "present"
    assert candidate.sections_detected["hypothetical_conditions_present"].value == "present"
    assert candidate.sections_detected["certification_section_present"].value == "present"
    assert candidate.sections_detected["limiting_conditions_section_present"].value == "present"


def test_extracts_table_style_label_variants_with_wide_spacing() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Appraisal Report
                Subject Property        100 Sample Avenue
                Property Classification  Office showroom
                Inspection Date         July 2, 2026
                Effective Date          July 3, 2026
                Prepared By             Alex Example
                Reviewed By             Riley Example
                """,
            ),
        )
    )

    assert candidate.fields["property_address"][0].value == "100 Sample Avenue"
    assert candidate.fields["property_type"][0].value == "Office showroom"
    assert candidate.fields["inspection_date"][0].value == "July 2, 2026"
    assert candidate.fields["effective_date"][0].value == "July 3, 2026"
    assert candidate.fields["appraiser_name"][0].value == "Alex Example"
    assert candidate.fields["reviewer_name"][0].value == "Riley Example"


def test_extracts_valid_single_space_label_tails_conservatively() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Appraisal Report
                Property Address 300 Sample Boulevard
                Date of Inspection September 5, 2026
                Review Appraiser Taylor Example
                """,
            ),
        )
    )

    assert candidate.fields["property_address"][0].value == "300 Sample Boulevard"
    assert candidate.fields["inspection_date"][0].value == "September 5, 2026"
    assert candidate.fields["reviewer_name"][0].value == "Taylor Example"


def test_rejects_ambiguous_single_space_label_tails() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Appraisal Report
                Subject Property is discussed throughout this synthetic report.
                Appraiser Certification
                Review Appraiser independence statement
                Inspection Date was not provided.
                """,
            ),
        )
    )

    assert candidate.fields["property_address"][0].confidence == "missing"
    assert candidate.fields["inspection_date"][0].confidence == "missing"
    assert candidate.fields["appraiser_name"][0].confidence == "missing"
    assert candidate.fields["reviewer_name"][0].confidence == "missing"


def test_extracts_additional_appraisal_label_variants() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Restricted Appraisal Report
                Address of Property: 200 Sample Road
                Date Inspected: August 4, 2026
                Principal Appraiser: Morgan Example
                Review Appraiser: Casey Example
                """,
            ),
        )
    )

    assert candidate.fields["property_address"][0].value == "200 Sample Road"
    assert candidate.fields["inspection_date"][0].value == "August 4, 2026"
    assert candidate.fields["appraiser_name"][0].value == "Morgan Example"
    assert candidate.fields["reviewer_name"][0].value == "Casey Example"


def test_detects_certification_section_variants() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(page_number=1, text="Appraisal Report"),
            PageText(page_number=3, text="Appraiser's Certification and Limiting Conditions"),
        )
    )

    assert candidate.sections_detected["certification_section_present"].value == "present"


def test_extracts_salient_facts_table_values() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Summary of Salient Facts
                Client
                Example Bank
                Effective Date of Value
                October 10, 2026
                Date of Inspection
                October 8, 2026
                Date of Report
                October 15, 2026
                Intended Use
                Loan underwriting
                """,
            ),
        )
    )

    assert candidate.fields["client"][0].value == "Example Bank"
    assert candidate.fields["effective_date"][0].value == "October 10, 2026"
    assert candidate.fields["inspection_date"][0].value == "October 8, 2026"
    assert candidate.fields["report_date"][0].value == "October 15, 2026"
    assert candidate.fields["intended_use"][0].value == "Loan underwriting"
    assert "summary of salient facts table" in candidate.fields["client"][0].extraction_method


def test_extracts_signature_and_review_blocks() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Certification of Appraisal
                Respectfully submitted,
                Alex Example
                Certified General Real Estate Appraiser

                Appraisal Review
                Reviewed by
                Riley Example
                Review Appraiser
                """,
            ),
        )
    )

    assert candidate.sections_detected["certification_section_present"].value == "present"
    assert candidate.fields["appraiser_name"][0].value == "Alex Example"
    assert "signature block" in candidate.fields["appraiser_name"][0].extraction_method
    assert candidate.fields["reviewer_name"][0].value == "Riley Example"
    assert "review section" in candidate.fields["reviewer_name"][0].extraction_method


def test_extracts_first_page_title_block_split_lines() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Real Estate
                Appraisal Report
                Prepared for Synthetic Client
                """,
            ),
        )
    )

    assert candidate.fields["report_title"][0].value == "Real Estate Appraisal Report"
    assert "first page title block" in candidate.fields["report_title"][0].extraction_method


def test_extracts_transmittal_section_signature_and_inspection_date() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Letter of Transmittal
                The property was inspected on November 2, 2026.
                Respectfully submitted,
                Morgan Example
                Certified General Real Estate Appraiser
                """,
            ),
        )
    )

    assert candidate.fields["inspection_date"][0].value == "November 2, 2026"
    assert "inspection anchor" in candidate.fields["inspection_date"][0].extraction_method
    assert candidate.fields["appraiser_name"][0].value == "Morgan Example"
    assert "transmittal section" in candidate.fields["appraiser_name"][0].extraction_method


def test_extracts_certification_signature_section_appraiser() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=5,
                text="""
                Appraiser Certification
                I certify that the analyses are synthetic.
                Signed:
                Taylor Example
                State Certified General Appraiser
                """,
            ),
        )
    )

    assert candidate.fields["appraiser_name"][0].value == "Taylor Example"
    assert "certification signature section" in candidate.fields["appraiser_name"][0].extraction_method


def test_extracts_review_signature_section_reviewer() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=6,
                text="""
                Review Certification
                Review Signed:
                Casey Example
                Review Appraiser
                """,
            ),
        )
    )

    assert candidate.fields["reviewer_name"][0].value == "Casey Example"
    assert "review signature section" in candidate.fields["reviewer_name"][0].extraction_method


def test_extracts_inspection_anchor_wording_without_label() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=2,
                text="The subject was observed during a site visit conducted December 3, 2026.",
            ),
        )
    )

    assert candidate.fields["inspection_date"][0].value == "December 3, 2026"
    assert "inspection anchor" in candidate.fields["inspection_date"][0].extraction_method


def test_signature_blocks_conflict_when_multiple_unlabeled_people_are_plausible() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Certification of Appraisal
                Alex Example
                Certified General Real Estate Appraiser
                Morgan Example
                Certified General Real Estate Appraiser
                """,
            ),
        )
    )

    assert {item.confidence for item in candidate.fields["appraiser_name"]} == {"conflicting"}


def test_marks_conflicting_field_candidates() -> None:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(page_number=1, text="Client: Example Bank"),
            PageText(page_number=2, text="Client: Example Credit Union"),
        )
    )

    assert {item.confidence for item in candidate.fields["client"]} == {"conflicting"}
    assert len(candidate.fields["client"]) == 2


def test_marks_missing_fields_without_guessing() -> None:
    candidate = extract_report_metadata_from_pages((PageText(page_number=1, text="Appraisal Report"),))

    assert candidate.fields["client"][0].confidence == "missing"
    assert candidate.fields["effective_date"][0].confidence == "missing"
    assert candidate.approaches_referenced["income_approach"].confidence == "missing"


def test_inventory_handoff_considers_likely_final_pdfs_and_docx(tmp_path: Path) -> None:
    intake_path = tmp_path / "historical-intake-report.json"
    final_pdf = tmp_path / "missing-final.pdf"
    final_docx = tmp_path / "missing-final.docx"
    intake_path.write_text(
        """
        {
          "files": [
            {
              "file_id": "final-pdf",
              "file_path": "%s",
              "file_name": "Final Report.pdf",
              "extension": ".pdf",
              "candidate_role": "final_report"
            },
            {
              "file_id": "draft-pdf",
              "file_path": "ignored-draft.pdf",
              "file_name": "Draft Report.pdf",
              "extension": ".pdf",
              "candidate_role": "draft_report"
            },
            {
              "file_id": "final-docx",
              "file_path": "%s",
              "file_name": "Final Report.docx",
              "extension": ".docx",
              "candidate_role": "final_report"
            }
          ]
        }
        """
        % (str(final_pdf).replace("\\", "\\\\"), str(final_docx).replace("\\", "\\\\")),
        encoding="utf-8",
    )

    report = run_historical_knowledge_extraction(intake_path)

    assert [candidate.file_id for candidate in report.report_candidates] == ["final-pdf", "final-docx"]
    assert report.report_candidates[0].extraction_status == "no_searchable_text"
    assert report.report_candidates[1].extraction_status == "no_searchable_text"


def test_inventory_handoff_carries_safe_metadata_candidates(tmp_path: Path) -> None:
    intake_path = tmp_path / "historical-intake-report.json"
    final_pdf = tmp_path / "missing-final.pdf"
    intake_path.write_text(
        """
        {
          "files": [
            {
              "file_id": "final-pdf",
              "file_path": "%s",
              "file_name": "Final Report.pdf",
              "extension": ".pdf",
              "candidate_role": "final_report",
              "likely_property_address": "100 Sample Street",
              "likely_report_type": "appraisal report",
              "likely_report_date": "2026"
            }
          ]
        }
        """
        % str(final_pdf).replace("\\", "\\\\"),
        encoding="utf-8",
    )

    report = run_historical_knowledge_extraction(intake_path)
    candidate = report.report_candidates[0]

    assert candidate.fields["property_address"][0].value == "100 Sample Street"
    assert candidate.fields["property_address"][0].confidence == "medium"
    assert candidate.fields["property_address"][0].source_hint == "intake filename/folder metadata"
    assert candidate.fields["report_type"][0].value == "appraisal report"
    assert candidate.fields["report_date"][0].value == "2026"


def test_embedded_pdf_text_reports_actionable_missing_library_warning(tmp_path: Path) -> None:
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF synthetic placeholder")

    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "pypdf":
            raise ImportError("synthetic missing pypdf")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        pages, warnings = _extract_embedded_pdf_text(pdf_path)

    assert pages == ()
    assert warnings == (PYPDF_MISSING_WARNING,)


def test_embedded_pdf_text_reads_searchable_pages_with_synthetic_reader(tmp_path: Path) -> None:
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF synthetic placeholder")
    fake_module = _fake_pypdf_module(("Synthetic searchable page", ""))

    with patch.dict(sys.modules, {"pypdf": fake_module}):
        pages, warnings = _extract_embedded_pdf_text(pdf_path)

    assert warnings == ()
    assert pages == (PageText(page_number=1, text="Synthetic searchable page"),)


def test_embedded_pdf_text_warns_when_no_searchable_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF synthetic placeholder")
    fake_module = _fake_pypdf_module(("", None))

    with patch.dict(sys.modules, {"pypdf": fake_module}):
        pages, warnings = _extract_embedded_pdf_text(pdf_path)

    assert pages == ()
    assert warnings == ("no embedded/searchable PDF text found; OCR was not attempted",)


def test_embedded_docx_text_reports_actionable_missing_library_warning(tmp_path: Path) -> None:
    docx_path = tmp_path / "synthetic.docx"
    docx_path.write_bytes(b"synthetic docx placeholder")
    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "docx":
            raise ImportError("synthetic missing python-docx")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        pages, warnings = _extract_embedded_docx_text(docx_path, source_label="docx companion source: synthetic-docx")

    assert pages == ()
    assert warnings == (PYTHON_DOCX_MISSING_WARNING,)


def test_embedded_docx_text_reads_synthetic_paragraphs(tmp_path: Path) -> None:
    docx_path = tmp_path / "synthetic.docx"
    docx_path.write_bytes(b"synthetic docx placeholder")

    with patch.dict(sys.modules, {"docx": _fake_docx_module(("Appraisal Report", "Property Address: 100 Sample Street"))}):
        pages, warnings = _extract_embedded_docx_text(docx_path, source_label="docx companion source: synthetic-docx")

    assert warnings == ()
    assert pages == (PageText(page_number=1, text="Appraisal Report\nProperty Address: 100 Sample Street", source_label="docx companion source: synthetic-docx"),)


def test_docx_companion_enriches_pdf_report_group_without_summary_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "synthetic-final.pdf"
    docx_path = tmp_path / "synthetic-companion.docx"
    pdf_path.write_bytes(b"%PDF synthetic placeholder")
    docx_path.write_bytes(b"synthetic docx placeholder")
    intake_path = tmp_path / "historical-intake-report.json"
    intake_path.write_text(
        """
        {
          "files": [
            {
              "file_id": "final-pdf",
              "file_path": "%s",
              "file_name": "Final Report.pdf",
              "extension": ".pdf",
              "candidate_role": "final_report",
              "parent_folder": "%s"
            },
            {
              "file_id": "companion-docx",
              "file_path": "%s",
              "file_name": "Companion Source.docx",
              "extension": ".docx",
              "candidate_role": "source_document",
              "parent_folder": "%s"
            }
          ],
          "candidate_order_groups": [
            {
              "group_id": "synthetic-group",
              "file_ids": ["final-pdf", "companion-docx"],
              "likely_primary_report_file_id": "final-pdf"
            }
          ]
        }
        """
        % (
            str(pdf_path).replace("\\", "\\\\"),
            str(tmp_path).replace("\\", "\\\\"),
            str(docx_path).replace("\\", "\\\\"),
            str(tmp_path).replace("\\", "\\\\"),
        ),
        encoding="utf-8",
    )

    with patch.dict(
        sys.modules,
        {
            "pypdf": _fake_pypdf_module(("", None)),
            "docx": _fake_docx_module(
                (
                    "Restricted Appraisal Report",
                    "Property Address: 100 Sample Street",
                    "Client: Example Bank",
                    "Sales Comparison Approach",
                )
            ),
        },
    ):
        report = run_historical_knowledge_extraction(intake_path)

    candidate = report.report_candidates[0]
    summary = render_historical_knowledge_summary(report)

    assert candidate.extraction_status == "extracted"
    assert candidate.fields["property_address"][0].source_hint == "docx companion source: companion-docx"
    assert candidate.approaches_referenced["sales_comparison_approach"].source_hint == "docx companion source: companion-docx"
    assert "100 Sample Street" not in summary
    assert "Example Bank" not in summary


def test_summary_output_generation(tmp_path: Path) -> None:
    candidate = extract_report_metadata_from_pages(_synthetic_pages())
    report = HistoricalKnowledgeReport(
        knowledge_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_inventory_path="synthetic-intake.json",
        report_candidates=(candidate,),
    )

    outputs = save_historical_knowledge_outputs(report, tmp_path)

    assert Path(outputs["json"]).exists()
    assert Path(outputs["markdown"]).name == "historical-knowledge-summary.md"
    assert "deterministic metadata candidates only" in render_historical_knowledge_summary(report)


def _fake_pypdf_module(page_texts: tuple[str | None, ...]) -> ModuleType:
    module = ModuleType("pypdf")

    class FakePage:
        def __init__(self, text: str | None) -> None:
            self.text = text

        def extract_text(self) -> str | None:
            return self.text

    class FakeReader:
        def __init__(self, path: str) -> None:
            self.path = path
            self.pages = [FakePage(text) for text in page_texts]

    module.PdfReader = FakeReader  # type: ignore[attr-defined]
    return module


def _fake_docx_module(paragraph_texts: tuple[str, ...]) -> ModuleType:
    module = ModuleType("docx")

    class FakeParagraph:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeDocument:
        def __init__(self, path: str) -> None:
            self.path = path
            self.paragraphs = [FakeParagraph(text) for text in paragraph_texts]

    module.Document = FakeDocument  # type: ignore[attr-defined]
    return module
