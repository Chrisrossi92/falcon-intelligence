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

## Local Tooling and Production Gate

The repository contains read-only local historical inventory and embedded/searchable PDF and DOCX extraction tools. Their presence does not authorize use on arbitrary real files. Any approved local run must use an explicitly selected source scope, keep source files outside the repository, keep generated outputs under ignored local paths, and never print or commit extracted report text.

The OCR/layout pilot is disabled by default and diagnostic-only when explicitly enabled. It may emit redacted shapes and fingerprints but must not save page images, raw OCR text, snippets, or extracted values, and its results do not enter verification or firm knowledge.

The synthetic Local Intake Review and Assignment/Property Brief exporter requires an explicit output directory. It rejects tracked repository locations and permits repository-local output only under ignored `data/`, `exports/`, `local-data/`, or `local_data/` roots. AIR and brief exports are runtime artifacts and must not be committed.

Before any production ingestion, persisted real extracted facts, source preview, embeddings, external service, or expanded real-content workflow is enabled, the project must define:

- A local-only storage boundary.
- A synthetic test corpus.
- Redaction and logging rules.
- A review checklist for file handling.
- Clear user controls for selecting local folders.

See `docs/real-data-production-readiness-gate.md` and `docs/production-gate-review-packet-template.md` for the required production-readiness checklist and approval packet. Automated tests and CI must remain synthetic-only.
