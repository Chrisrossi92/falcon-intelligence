# Falcon Intelligence

Falcon Intelligence is a local-first prototype framework for an appraisal firm knowledge base.

This repository currently contains only the code and documentation scaffold. It must not contain real appraisal reports, client source documents, OneDrive files, extracted text, generated embeddings, or local data exports.

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
scripts/               Dependency-free smoke validation scripts
src/falcon_intel/       Framework package
tests/                 Tests and committed synthetic metadata fixtures
```

## Development Status

This is an initial scaffold. No ingestion, parsing, OCR, embedding, or retrieval code is active yet.

## Local Tests

Install development test tooling without adding runtime dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run the core local checks:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
PYTHONPATH=src python3 scripts/smoke_synthetic_fixtures.py
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_schema.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_snapshot.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_cli.py
PYTHONPATH=src python3 -m pytest
```
