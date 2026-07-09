"""Smoke check for local-only historical knowledge metadata extraction."""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
from unittest.mock import patch

from falcon_intel.historical_knowledge import (
    PYPDF_MISSING_WARNING,
    PYTHON_DOCX_MISSING_WARNING,
    PageText,
    _extract_embedded_docx_text,
    _extract_embedded_pdf_text,
    extract_report_metadata_from_pages,
    run_historical_knowledge_extraction,
    render_historical_knowledge_summary,
    save_historical_knowledge_outputs,
    HistoricalKnowledgeReport,
)


def main() -> int:
    candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Restricted Appraisal Report
                Property Address: 100 Sample Street
                Property Type: Industrial
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
                Sales Comparison Approach
                Income Approach
                Cost Approach
                Extraordinary Assumptions
                Hypothetical Conditions
                Certification
                General Assumptions and Limiting Conditions
                """,
            ),
        )
    )

    assert candidate.extraction_status == "extracted"
    assert candidate.fields["report_type"][0].value == "restricted appraisal report"
    assert candidate.fields["client"][0].value == "Example Bank"
    assert candidate.approaches_referenced["sales_comparison_approach"].value == "present"
    assert candidate.sections_detected["extraordinary_assumptions_present"].value == "present"

    table_candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Appraisal Report
                Subject Property        100 Sample Avenue
                Inspection Date         July 2, 2026
                Prepared By             Alex Example
                Reviewed By             Riley Example
                """,
            ),
            PageText(page_number=2, text="Appraiser's Certification"),
        )
    )
    assert table_candidate.fields["property_address"][0].value == "100 Sample Avenue"
    assert table_candidate.fields["inspection_date"][0].value == "July 2, 2026"
    assert table_candidate.fields["appraiser_name"][0].value == "Alex Example"
    assert table_candidate.fields["reviewer_name"][0].value == "Riley Example"
    assert table_candidate.sections_detected["certification_section_present"].value == "present"

    tuned_candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Market Value Appraisal Report
                Subject Property Address: 200 Example Road
                Site Visit Date: August 4, 2026
                Signed By: Morgan Example
                Review Completed By: Casey Example
                """,
            ),
        )
    )
    assert tuned_candidate.fields["report_title"][0].value == "Market Value Appraisal Report"
    assert tuned_candidate.fields["inspection_date"][0].value == "August 4, 2026"
    assert tuned_candidate.fields["appraiser_name"][0].value == "Morgan Example"
    assert tuned_candidate.fields["reviewer_name"][0].value == "Casey Example"

    single_space_candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Valuation Report
                Property Address 300 Example Avenue
                Inspected September 5, 2026
                Appraiser of Record Taylor Example
                Review Signed By Jordan Example
                """,
            ),
        )
    )
    assert single_space_candidate.fields["report_title"][0].value == "Valuation Report"
    assert single_space_candidate.fields["inspection_date"][0].value == "September 5, 2026"
    assert single_space_candidate.fields["appraiser_name"][0].value == "Taylor Example"
    assert single_space_candidate.fields["reviewer_name"][0].value == "Jordan Example"

    anchor_candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                Real Estate
                Appraisal Report
                Letter of Transmittal
                The property was inspected on November 2, 2026.
                Respectfully submitted,
                Avery Example
                Certified General Real Estate Appraiser
                """,
            ),
            PageText(
                page_number=5,
                text="""
                Review Certification
                Review Signed:
                Casey Example
                Review Appraiser
                """,
            ),
            PageText(
                page_number=6,
                text="The subject was observed during a site visit conducted December 3, 2026.",
            ),
        )
    )
    assert anchor_candidate.fields["report_title"][0].value == "Real Estate Appraisal Report"
    assert "first page title block" in anchor_candidate.fields["report_title"][0].extraction_method
    assert "inspection anchor" in anchor_candidate.fields["inspection_date"][0].extraction_method
    assert anchor_candidate.fields["appraiser_name"][0].value == "Avery Example"
    assert "appraiser credential anchor" in anchor_candidate.fields["appraiser_name"][0].extraction_method
    assert anchor_candidate.fields["reviewer_name"][0].value == "Casey Example"
    assert "review signature section" in anchor_candidate.fields["reviewer_name"][0].extraction_method

    fallback_anchor_candidate = extract_report_metadata_from_pages(
        (
            PageText(page_number=1, text="Cover page"),
            PageText(
                page_number=6,
                text="""
                Synthetic Market Value Appraisal Report
                Certified General Real Estate Appraiser
                Jordan Example
                """,
            ),
        )
    )
    assert fallback_anchor_candidate.fields["report_title"][0].value == "Synthetic Market Value Appraisal Report"
    assert "document title anchor" in fallback_anchor_candidate.fields["report_title"][0].extraction_method
    assert fallback_anchor_candidate.fields["appraiser_name"][0].value == "Jordan Example"
    assert "segmented appraiser credential anchor" in fallback_anchor_candidate.fields["appraiser_name"][0].extraction_method

    segmented_signature_candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=9,
                text="""
                Certification of Appraisal
                Synthetic Valuation Services LLC
                100 Example Street
                Phone: 555-0100
                Email: example@example.test
                License No. CG-000000
                Morgan Example, MAI
                State-Certified General Appraiser

                This intentionally long certification paragraph is not a person name and should not be selected as the appraiser candidate.
                """,
            ),
        )
    )
    appraiser_values = {item.value for item in segmented_signature_candidate.fields["appraiser_name"]}
    assert "Morgan Example, MAI" in appraiser_values
    assert all("LLC" not in str(value) for value in appraiser_values)
    assert all("555" not in str(value) for value in appraiser_values)
    assert all("License" not in str(value) for value in appraiser_values)

    following_signature_candidate = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=9,
                text="""
                Certification of Appraisal
                Signed By:
                Riley Example, AI-GRS
                Certified General Appraiser
                """,
            ),
        )
    )
    assert following_signature_candidate.fields["appraiser_name"][0].value == "Riley Example, AI-GRS"

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        report = HistoricalKnowledgeReport(
            knowledge_version="1",
            generated_at="2026-06-30T00:00:00+00:00",
            source_inventory_path="synthetic-intake.json",
            report_candidates=(candidate,),
        )
        outputs = save_historical_knowledge_outputs(report, temp_path)
        assert Path(outputs["json"]).exists()
        assert Path(outputs["markdown"]).exists()
        assert "deterministic metadata candidates only" in render_historical_knowledge_summary(report)

        pdf_path = temp_path / "synthetic.pdf"
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

        with patch.dict(sys.modules, {"pypdf": _fake_pypdf_module(("Synthetic searchable page", ""))}):
            pages, warnings = _extract_embedded_pdf_text(pdf_path)
        assert pages == (PageText(page_number=1, text="Synthetic searchable page"),)
        assert warnings == ()

        with patch.dict(sys.modules, {"pypdf": _fake_pypdf_module(("", None))}):
            pages, warnings = _extract_embedded_pdf_text(pdf_path)
        assert pages == ()
        assert warnings == ("no embedded/searchable PDF text found; OCR was not attempted",)

        docx_path = temp_path / "synthetic-companion.docx"
        docx_path.write_bytes(b"synthetic docx placeholder")

        def fake_docx_missing_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "docx":
                raise ImportError("synthetic missing python-docx")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_docx_missing_import):
            pages, warnings = _extract_embedded_docx_text(docx_path, source_label="docx companion source: synthetic-docx")
        assert pages == ()
        assert warnings == (PYTHON_DOCX_MISSING_WARNING,)

        docx_text = (
            "Restricted Appraisal Report",
            "Property Address: 100 Sample Street",
            "Client: Example Bank",
            "Sales Comparison Approach",
        )
        with patch.dict(sys.modules, {"docx": _fake_docx_module(docx_text)}):
            pages, warnings = _extract_embedded_docx_text(docx_path, source_label="docx companion source: synthetic-docx")
        assert warnings == ()
        assert pages[0].source_label == "docx companion source: synthetic-docx"
        assert "100 Sample Street" in pages[0].text

        intake_path = temp_path / "historical-intake-report.json"
        intake_path.write_text(
            f"""
            {{
              "files": [
                {{
                  "file_id": "synthetic-final",
                  "file_path": "{str(pdf_path).replace(chr(92), chr(92) + chr(92))}",
                  "file_name": "Final Report.pdf",
                  "extension": ".pdf",
                  "candidate_role": "final_report",
                  "likely_property_address": "100 Sample Street",
                  "likely_report_type": "appraisal report",
                  "likely_report_date": "2026"
                }}
              ]
            }}
            """,
            encoding="utf-8",
        )
        with patch.dict(sys.modules, {"pypdf": _fake_pypdf_module(("", None))}):
            intake_report = run_historical_knowledge_extraction(intake_path)
        intake_candidate = intake_report.report_candidates[0]
        assert intake_candidate.fields["property_address"][0].value == "100 Sample Street"
        assert intake_candidate.fields["property_address"][0].source_hint == "intake filename/folder metadata"

        companion_intake_path = temp_path / "historical-intake-with-docx-report.json"
        unrelated_docx_path = temp_path / "unrelated-companion.docx"
        unrelated_docx_path.write_bytes(b"unrelated synthetic docx placeholder")
        companion_intake_path.write_text(
            f"""
            {{
              "files": [
                {{
                  "file_id": "synthetic-final",
                  "file_path": "{str(pdf_path).replace(chr(92), chr(92) + chr(92))}",
                  "file_name": "Final Report.pdf",
                  "extension": ".pdf",
                  "candidate_role": "final_report",
                  "parent_folder": "{str(temp_path).replace(chr(92), chr(92) + chr(92))}"
                }},
                {{
                  "file_id": "synthetic-docx",
                  "file_path": "{str(docx_path).replace(chr(92), chr(92) + chr(92))}",
                  "file_name": "Companion Source.docx",
                  "extension": ".docx",
                  "candidate_role": "source_document",
                  "parent_folder": "{str(temp_path).replace(chr(92), chr(92) + chr(92))}"
                }},
                {{
                  "file_id": "unrelated-docx",
                  "file_path": "{str(unrelated_docx_path).replace(chr(92), chr(92) + chr(92))}",
                  "file_name": "Unrelated Source.docx",
                  "extension": ".docx",
                  "candidate_role": "source_document",
                  "parent_folder": "{str(temp_path).replace(chr(92), chr(92) + chr(92))}"
                }}
              ],
              "candidate_order_groups": [
                {{
                  "group_id": "synthetic-group",
                  "file_ids": ["synthetic-final", "synthetic-docx"],
                  "likely_primary_report_file_id": "synthetic-final"
                }}
              ]
            }}
            """,
            encoding="utf-8",
        )
        with patch.dict(sys.modules, {"pypdf": _fake_pypdf_module(("", None)), "docx": _fake_docx_module(docx_text)}):
            companion_report = run_historical_knowledge_extraction(companion_intake_path)
        companion_candidate = companion_report.report_candidates[0]
        assert companion_candidate.extraction_status == "extracted"
        assert companion_candidate.fields["property_address"][0].value == "100 Sample Street"
        assert companion_candidate.fields["property_address"][0].source_hint == "docx companion source: synthetic-docx"
        assert "unrelated-docx" not in str(companion_candidate.fields)
        assert companion_candidate.approaches_referenced["sales_comparison_approach"].source_hint == "docx companion source: synthetic-docx"
        companion_summary = render_historical_knowledge_summary(companion_report)
        assert "100 Sample Street" not in companion_summary
        assert "Example Bank" not in companion_summary

    print("historical knowledge smoke validation passed")
    return 0


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


if __name__ == "__main__":
    raise SystemExit(main())
