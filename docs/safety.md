# Data Safety Policy

Falcon Intelligence must be developed without committing or exposing client files, appraisal reports, or local OneDrive content.

## Prohibited Repository Content

- Appraisal reports and workfiles.
- PDFs, Word documents, spreadsheets, CSVs, TSVs, and text exports.
- OCR output, extracted text, embeddings, indexes, databases, and vector stores.
- Any document copied from OneDrive or another local client file location.

## Allowed Repository Content

- Source code.
- Documentation.
- Synthetic test fixtures that do not resemble real client material.
- Configuration templates that contain no secrets or real paths.

## Future Ingestion Gate

Before any ingestion code is enabled, the project should define:

- A local-only storage boundary.
- A synthetic test corpus.
- Redaction and logging rules.
- A review checklist for file handling.
- Clear user controls for selecting local folders.

See `docs/real-data-production-readiness-gate.md` for the required production-readiness checklist before any real report content, extraction, OCR, embeddings, or source-document preview is allowed.
