# Falcon OCR/Layout Feasibility Planning

This note defines a planning layer only. It does not authorize OCR, page-image export, raw OCR text storage, AI extraction, embeddings, uploads, source preview, or production ingestion.

## Current Unresolved Targets

The current deterministic pipeline has already improved searchable PDF/DOCX extraction, companion DOCX support, section anchors, report-title extraction, evidence ledgers, and promotion readiness. The remaining unresolved target fields are:

- `inspection_date`
- `reviewer_name`
- `appraiser_name`
- `report_title` only if it regresses in a future run

Current diagnostics show that `inspection_date` and `reviewer_name` anchor families are absent from searchable text. `appraiser_name` anchor families are present, but searchable text around those anchors does not consistently yield clean person-name lines.

## Why Searchable Text Is Insufficient

Searchable embedded text is still the safest first pass, but it loses layout information that matters for signature and review areas:

- Signature names can be positioned near lines, stamps, seals, or credentials instead of adjacent text.
- Reviewer labels may appear in scanned certification pages or image-only signature blocks.
- Inspection and site-visit dates may exist in forms, cover letters, or scanned pages that do not expose searchable anchors.
- Extracted line order can merge company names, addresses, license lines, and certification paragraphs into long noisy candidates.

The feasibility layer should therefore answer whether OCR/layout extraction is worth building, not perform OCR itself.

## Local-Only Outputs

Feasibility reports should stay under ignored local folders:

```text
data/ocr-feasibility/
```

Future OCR/layout experiments, if explicitly approved, should use separate ignored folders:

```text
data/ocr-layout/
data/ocr-cache/
data/ocr-redacted-diagnostics/
```

Raw OCR text, page images, screenshots, crops, and source snippets must not be committed. Any future temporary OCR text should be local-only, ignored, and either ephemeral or governed by an explicit retention rule.

## Privacy Risks

OCR raises higher privacy risk than embedded-text diagnostics because it can expose image-only signatures, names, client data, addresses, stamps, seals, handwritten notes, and certification blocks. The main risks are:

- Accidentally saving raw OCR text.
- Accidentally saving page screenshots or crops.
- Printing snippets during debugging.
- Treating OCR output as authoritative without source-tier and confidence controls.
- Promoting image-derived values without human review.

Future OCR diagnostics should report only anonymous report indexes, page buckets, field families, coarse candidate shapes, length buckets, confidence labels, rejection reasons, and fingerprints.

## Dependency Options

Potential future options, all opt-in:

- Local Tesseract through `pytesseract` for simple OCR experiments.
- `ocrmypdf` for searchable-PDF generation when allowed by retention policy.
- PDF rasterization through Poppler or PyMuPDF for page images or layout analysis.
- Cloud OCR only after a separate privacy, legal, and data-processing review.

The pilot uses optional Python wrappers only when installed:

- `pymupdf` for in-memory PDF page rasterization.
- `pytesseract` for the Python OCR wrapper.
- `Pillow` for image handoff.

The Tesseract executable must still be installed separately on the Windows machine. The base and development installs do not include these OCR dependencies.

## Why OCR Must Be Opt-In

OCR converts visually present report content into text. That crosses a stricter boundary than metadata scanning or privacy-safe aggregate diagnostics. It should remain opt-in because:

- It may reveal private report text that embedded extraction did not expose.
- It can generate large local artifacts that are easy to mishandle.
- It needs dependency, retention, and deletion rules.
- It needs human review before any field promotion.
- It should be scoped to known unresolved fields and page buckets, not whole-report extraction by default.

## Recommended Future Slice

The first implementation slice is a layout-only pilot:

- Do not run whole-report OCR.
- Limit processing to anonymous report indexes with missing `inspection_date` or `reviewer_name`.
- Limit pages to recommended buckets from `data/ocr-feasibility/ocr-feasibility-report.json`.
- Emit only redacted diagnostics: page bucket, target field, anchor family, candidate shape, length bucket, confidence tier, and rejection reason.
- Keep raw OCR text and page images out of committed files and out of terminal output.
- Keep OCR-derived diagnostics out of verification and promotion until a separate review/promotion slice is approved.
