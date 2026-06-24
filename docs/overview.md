# Falcon Intelligence Overview

Falcon Intelligence is planned as a local-first knowledge base for appraisal firm workflows.

The initial repository is intentionally limited to framework code and documentation. Future work may add controlled ingestion, extraction, indexing, and retrieval, but those features are out of scope for this scaffold.

## Goals

- Keep private appraisal material local and out of version control.
- Provide a clear place for future knowledge-base services.
- Separate core framework code from future premium capabilities.
- Make safety checks explicit before any document pipeline is added.

## Non-Goals

- No real report ingestion.
- No sample appraisal documents.
- No OCR, parsing, embedding, vector storage, or search implementation.
- No cloud sync or external data transfer.

See `docs/session-handoff-roadmap.md` for the current implementation checkpoint, validation commands, known risks, and recommended next slices.

See `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md` for the canonical long-range product roadmap.

See `docs/real-data-production-readiness-gate.md` and complete `docs/production-gate-review-packet-template.md` before considering any real report content, extraction, OCR, embeddings, or source-document preview.
