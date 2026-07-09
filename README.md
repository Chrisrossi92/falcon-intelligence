# Falcon Intelligence

Falcon Intelligence is a local-first prototype framework for an appraisal firm knowledge base.

This repository currently contains only the code and documentation scaffold. It must not contain real appraisal reports, client source documents, OneDrive files, extracted text, generated embeddings, or local data exports.

The canonical long-range product roadmap is `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md`.

The canonical Intelligence Engine architecture is `docs/architecture/FALCON_INTELLIGENCE_ENGINE.md`, with the architecture index at `docs/architecture/README.md`.

## Current Scope

- Define the safety boundary for future local document processing.
- Provide a framework for a future premium module.
- Keep ingestion adapters disabled until explicit review and approval.
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

This is an initial scaffold. No ingestion, parsing, OCR, embedding, or retrieval code is active yet.

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

Run the core local checks:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
PYTHONPATH=src python3 scripts/smoke_synthetic_fixtures.py
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_schema.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_snapshot.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_cli.py
PYTHONPATH=src python3 scripts/smoke_falcon_api_contract.py
PYTHONPATH=src python3 scripts/smoke_match_audit.py
PYTHONPATH=src python3 scripts/smoke_audit_event_snapshots.py
PYTHONPATH=src python3 scripts/smoke_map_workspace.py
PYTHONPATH=src python3 scripts/smoke_map_workspace_snapshot.py
PYTHONPATH=src python3 scripts/smoke_historical_comp.py
PYTHONPATH=src python3 scripts/smoke_historical_intake.py
PYTHONPATH=src python3 scripts/smoke_historical_knowledge.py
PYTHONPATH=src python3 scripts/smoke_verification_engine.py
PYTHONPATH=src python3 scripts/smoke_knowledge_objects.py
PYTHONPATH=src python3 scripts/smoke_memory_graph.py
PYTHONPATH=src python3 scripts/smoke_evidence_links.py
PYTHONPATH=src python3 scripts/smoke_data_passport.py
PYTHONPATH=src python3 scripts/smoke_data_passport_lookup.py
PYTHONPATH=src python3 scripts/smoke_falcon_passport_contract.py
PYTHONPATH=src python3 scripts/smoke_passport_detail_drawer.py
PYTHONPATH=src python3 scripts/smoke_falcon_evidence_contract.py
PYTHONPATH=src python3 scripts/smoke_schema_registry.py
PYTHONPATH=src python3 scripts/smoke_api_envelope_snapshots.py
PYTHONPATH=src python3 scripts/smoke_permission_policy.py
PYTHONPATH=src python3 scripts/smoke_falcon_permission_contracts.py
PYTHONPATH=src python3 scripts/smoke_synthetic_workflow.py
PYTHONPATH=src python3 -m pytest
```

## CI

GitHub Actions runs the same synthetic-only validation on every push and pull request with Python 3.12. CI installs `.[dev]`, compiles `src`, `scripts`, and `tests`, runs the synthetic smoke checks, and runs pytest. It does not use OneDrive or real report data.
