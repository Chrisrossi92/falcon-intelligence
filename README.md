# Falcon Intelligence

Falcon Intelligence is a local-first appraisal intelligence prototype for turning controlled evidence into verified, provenance-rich firm knowledge.

The repository contains synthetic product contracts and UI previews plus controlled local tooling for historical inventory, embedded/searchable PDF and DOCX extraction, deterministic verification, Knowledge Object candidates, Memory Graph candidates, and privacy-safe extraction diagnostics. It must not contain real appraisal reports, client source documents, OneDrive files, extracted text, generated embeddings, local databases, or generated local outputs.

The canonical long-range product roadmap is `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md`.

The canonical Intelligence Engine architecture is `docs/architecture/FALCON_INTELLIGENCE_ENGINE.md`, with the architecture index at `docs/architecture/README.md`.

## Current Scope

- Maintain explicit safety boundaries for local document processing.
- Provide a framework for a future premium module.
- Keep production ingestion, cloud transfer, AI extraction, embeddings, and source preview disabled until explicit review and approval.
- Preserve local-first assumptions without committing private data.

## Safety Rules

- Do not copy appraisal reports or OneDrive files into this repository.
- Do not commit PDFs, Word files, spreadsheets, CSVs, extracted text, OCR output, vector stores, databases, or source exports.
- Keep all future local data outside the repository or under ignored paths.
- Use fixtures only when they are synthetic and clearly marked as synthetic.
- Develop without private drive access by using the committed synthetic fixtures under `tests/fixtures/`.

## Repository Layout

```text
docs/                  Project documentation and safety notes
docs/architecture/     Permanent Intelligence Engine architecture foundations
scripts/               Dependency-free smoke validation scripts
src/falcon_intel/       Framework package
tests/                 Tests and committed synthetic metadata fixtures
```

## Development Status

This is a controlled local prototype, not a complete production appraisal workflow. Embedded/searchable PDF and DOCX extraction is implemented for likely final reports and same-order DOCX companions selected through the historical-intake workflow. It is deterministic, read-only, stores no full report text, and writes derived outputs only to ignored local paths.

An OCR/layout pilot is also implemented, but it is opt-in and diagnostic-only. Without `--enable-ocr` it performs availability planning only; with the flag it is restricted to approved page buckets and emits redacted shapes and fingerprints rather than raw OCR text. OCR results are not promoted into verification or firm knowledge.

Production ingestion, cloud sync, AI extraction, embeddings, vector search, source-document preview, and report generation are not implemented.

The current synthetic Report Field Registry and Subject Profile preview are documented in `docs/report-field-registry.md`. They use demo data only and do not generate reports.

The synthetic Property Library and Controlled Comp Vault foundation is documented in `docs/property-library.md`. It uses demo property, evidence, report usage, and candidate match records only.

The synthetic Evidence Correction and Audit Trail foundation is available through `falcon-intel correction-audit`. It preserves prior values, corrected values, supporting evidence references, confidence impact, and audit event history with demo data only.

The local Historical Report Intake Inventory is documented in `docs/architecture/FALCON_HISTORICAL_INTAKE_PIPELINE.md`. It scans configured folders read-only and produces ignored local inventory reports without parsing document bodies or modifying source files.

## Local Tests

Install development test tooling without adding runtime dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

For local searchable-PDF extraction during historical sample calibration, install the optional PDF extra:

```bash
python3 -m pip install -e ".[pdf]"
```

This enables embedded/searchable PDF text extraction only. It does not enable OCR, AI extraction, embeddings, uploads, or storage of full report text.

For local DOCX extraction during historical sample calibration, install the optional DOCX extra:

```bash
python3 -m pip install -e ".[docx]"
```

This enables embedded DOCX text extraction for likely final DOCX files and same-order DOCX companions only. It does not enable OCR, AI extraction, embeddings, uploads, or storage of full report text.

For the opt-in local OCR/layout pilot, install the optional OCR Python wrappers and install the Tesseract executable separately on the Windows machine:

```bash
python3 -m pip install -e ".[ocr]"
```

The OCR pilot remains diagnostic-only. It must be run with an explicit `--enable-ocr` flag, processes only approved page buckets for `inspection_date` and `reviewer_name`, and writes only redacted shape/fingerprint diagnostics under ignored `data/` paths. It does not promote OCR results into verification, knowledge objects, or memory graph records.

Run the complete local validation suite. The smoke runner discovers every `scripts/**/smoke_*.py` entry point, so the list cannot drift when a new smoke check is added:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
python3 scripts/check_repository_safety.py
python3 scripts/run_smoke_suite.py
PYTHONPATH=src python3 -m pytest
cd frontend
npm ci
npm run typecheck
npm test -- --configLoader runner
npm run build -- --configLoader runner
```

## CI

GitHub Actions runs separate backend/repository and frontend validation jobs on every push and pull request. Backend CI installs `.[dev]`, compiles Python, enforces repository safety/privacy rules, discovers and runs the complete smoke suite, and runs pytest. Frontend CI uses `npm ci` with the committed lockfile, then runs TypeScript validation, frontend tests, and the production build. CI remains synthetic-only and does not use OneDrive, real report data, or external services.
