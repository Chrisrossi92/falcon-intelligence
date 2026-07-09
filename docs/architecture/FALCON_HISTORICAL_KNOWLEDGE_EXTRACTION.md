# Falcon Historical Knowledge Extraction

This document defines Phase 1 Historical Knowledge Extraction for Falcon Intelligence. This phase is local-only, deterministic, and limited to basic metadata candidates from likely final reports already identified by Historical Intake.

It does not authorize OCR, AI extraction, embeddings, vector databases, Supabase schemas, production APIs, uploads, source-file modification, full report analysis, supporting-document parsing, or Memory Graph creation.

## Position in the Architecture

Historical Knowledge Extraction sits after Historical Intake and before verification and Knowledge Object candidates:

```text
Historical folders
-> Historical Intake Inventory
-> Likely final report candidates
-> Deterministic metadata candidates
-> Verification Engine
-> Knowledge Object Builder
-> Future Memory Graph
```

This phase answers:

```text
What does this report appear to be?
```

It does not answer:

```text
What does this appraisal mean?
```

## Boundary Definitions

| Layer | Purpose | Current Phase 1 Status |
| --- | --- | --- |
| Inventory | Find files, classify roles, group packages, detect duplicates. | Existing Historical Intake. |
| Classification | Identify likely final reports and supporting files from metadata. | Existing Historical Intake. |
| Metadata extraction | Read searchable final-report text for conservative report descriptors. | Phase 1 scope. |
| Facts | Verified assertions suitable for the Intelligence Engine. | Verification Engine. |
| Knowledge object candidates | Local Property, Report, Client/User, Personnel, and Open Issues candidates built from Verified Facts. | Knowledge Object Builder V1. |
| Memory Graph | Connected institutional knowledge across assignments. | Future work. |

## Extraction Scope

Phase 1 operates only on likely final report files from the ignored historical intake JSON output. It currently targets PDF files and attempts embedded/searchable text extraction only when a local PDF text library is available.

If embedded text is unavailable, the extractor records a warning and stops. It must not OCR scanned PDFs.

Local searchable-PDF support is optional. Install it only for approved local sample calibration:

```bash
python -m pip install -e ".[pdf]"
```

This enables embedded text reads through `pypdf` only. It does not authorize OCR, full-text storage, AI extraction, embeddings, uploads, source-document preview, or production ingestion.

Supported metadata candidate fields:

- Report title.
- Report type.
- Property address.
- Property type.
- Client.
- Intended user.
- Intended use.
- Effective date.
- Report date.
- Inspection date.
- Appraiser name.
- Reviewer name.
- Sales comparison approach referenced.
- Income approach referenced.
- Cost approach referenced.
- Extraordinary assumptions present.
- Hypothetical conditions present.
- Certification section present.
- Limiting conditions section present.

Each candidate records:

- Value.
- Confidence label.
- Extraction method.
- Source hint such as page number.
- Warning when missing or conflicting.

## Confidence Labels

Phase 1 uses simple labels only:

- High.
- Medium.
- Low.
- Missing.
- Conflicting.

It does not implement scoring. If multiple deterministic candidates conflict, the field is marked conflicting and all short candidate values are retained.

## Why Deterministic First

Deterministic metadata extraction comes before AI or OCR because it creates a safe baseline:

- It proves local workfile access and reporting boundaries.
- It exercises the intake-to-extraction handoff.
- It reveals common report label patterns.
- It avoids hallucinated metadata.
- It avoids storing full report text.
- It keeps future AI/OCR design grounded in observable failure modes.

## Privacy and Safety Rules

The extractor must:

- Remain read-only.
- Operate only on likely final report candidates.
- Avoid OCR.
- Avoid AI calls.
- Avoid embeddings and vector stores.
- Avoid Supabase, production APIs, and uploads.
- Avoid source-file modification.
- Avoid parsing supporting documents.
- Avoid storing full report text in generated outputs.
- Keep generated outputs under ignored local directories.
- Convert real pattern observations into anonymized synthetic tests.

Generated outputs should be written under:

```text
data/historical-knowledge/
```

Expected local files:

```text
historical-knowledge-report.json
historical-knowledge-summary.md
```

## Future Direct-Upload Workfile Discipline

Future Falcon Intelligence uploads should preserve a complete, auditable workfile structure instead of relying on ad hoc folder contents.

Preferred future assignment package:

- Final report.
- Engagement letter.
- Source documents.
- Rent roll and financials.
- Maps.
- Photos.
- Comparable data.
- Reviewer notes.
- Revision history.

This is not implemented in Phase 1. The purpose is to establish discipline so future orders are easier to audit, extract, verify, and remember.

## Current Guardrail

Phase 1 produces metadata candidates only. A candidate is not a verified fact, knowledge object, insight, recommendation, action, or Memory Graph node until a future verification layer explicitly promotes it.

The permanent verification boundary is defined in `FALCON_VERIFICATION_ENGINE.md`. Historical Knowledge Extraction should feed that engine; it should not promote candidates directly into facts or Knowledge Model objects. Knowledge Object Builder V1 is the next local step after verification and is documented in `FALCON_KNOWLEDGE_OBJECT_BUILDER.md`.
