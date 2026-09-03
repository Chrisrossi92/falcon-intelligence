# Falcon Intelligence Overview

Falcon Intelligence is planned as a local-first knowledge base for appraisal firm workflows.

The repository combines synthetic product contracts and UI previews with controlled local historical-intake, embedded-text extraction, deterministic verification, canonical Assignment Intelligence Record V1 composition, Knowledge Object, Memory Graph, and diagnostic tooling. These foundations are not a complete production appraisal workflow.

The canonical Intelligence Engine architecture is documented in `docs/architecture/FALCON_INTELLIGENCE_ENGINE.md`. It establishes the permanent hierarchy:

```text
Documents
-> Facts
-> Knowledge
-> Insights
-> Recommendations
-> Actions
```

All future AI work should build on that hierarchy and the supporting knowledge, insight, and confidence models in `docs/architecture/`.

## Goals

- Keep private appraisal material local and out of version control.
- Provide a clear place for future knowledge-base services.
- Separate core framework code from future premium capabilities.
- Keep document pipelines local, bounded, auditable, and outside version control.

## Non-Goals

- No real report ingestion.
- No sample appraisal documents.
- No production ingestion, AI extraction, embedding, vector storage, source preview, or production search.
- No default OCR. The opt-in OCR/layout pilot emits redacted diagnostics only and does not promote results.
- No cloud sync or external data transfer.

## Implemented Local Tooling

- Read-only historical file inventory and candidate grouping.
- Embedded/searchable text extraction from approved likely-final PDFs, likely-final DOCX files, and same-order DOCX companions.
- Deterministic candidate extraction, verification ledgers, Knowledge Object candidates, and Memory Graph candidates.
- Assignment Intelligence Record V1 with explicit human decisions, provenance-preserving fact history, bounded knowledge references, and deterministic analysis readiness.
- Privacy-safe extraction, anchor, OCR-feasibility, and opt-in OCR/layout diagnostics.

All generated outputs stay under ignored local paths. Real reports and derived report text must never be committed.

See `docs/session-handoff-roadmap.md` for the current implementation checkpoint, validation commands, known risks, and recommended next slices.

See `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md` for the canonical long-range product roadmap.

See `docs/architecture/README.md` for the permanent Intelligence Engine architecture index.

See `docs/architecture/FALCON_ASSIGNMENT_INTELLIGENCE_RECORD.md` for the current canonical assignment record contract and model audit.

See `docs/real-data-production-readiness-gate.md` and complete `docs/production-gate-review-packet-template.md` before considering any real report content, extraction, OCR, embeddings, or source-document preview.
