# Development Notes

## Setup

This scaffold keeps runtime dependencies empty. Install the package itself for normal local development, or install the `dev` extra when you need the full pytest suite.

macOS:

```bash
python3 -m pip install -e .
python3 -m pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
python -m pip install -e .
python -m pip install -e ".[dev]"
```

## Checks

Future checks should include:

- Unit tests for safety guards.
- Static checks for accidental data paths.
- Validation that ignored document formats remain excluded.

Current dependency-free smoke validation:

```powershell
$env:PYTHONPATH='src'; python scripts/smoke_metadata_scan.py
$env:PYTHONPATH='src'; python scripts/smoke_manifest.py
$env:PYTHONPATH='src'; python scripts/smoke_manifest_search.py
$env:PYTHONPATH='src'; python scripts/smoke_assignment_discovery.py
$env:PYTHONPATH='src'; python scripts/smoke_assignment_profile.py
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_fixtures.py
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_intelligence_matcher.py
$env:PYTHONPATH='src'; python scripts/smoke_cli.py
```

## Test Commands

macOS:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
PYTHONPATH=src python3 scripts/smoke_synthetic_fixtures.py
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
PYTHONPATH=src python3 -m pytest
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src'; python -m compileall -q src scripts tests
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_fixtures.py
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_intelligence_matcher.py
$env:PYTHONPATH='src'; python -m pytest
```

## Fixture Policy

Tests may use synthetic fixtures only. Do not create fixtures from real reports, client records, OneDrive exports, or extracted report text.

## Developing Without OneDrive Access

Local development does not require access to any private drive or production document tree. Use the committed synthetic fixtures instead:

- Placeholder sample files: `tests/fixtures/synthetic_sample_data/`
- Committed manifest: `tests/fixtures/synthetic_manifests/synthetic-sample-intelligence-manifest.json`
- Committed assignment profiles: `tests/fixtures/synthetic_profiles/`

The placeholder files are intentionally tiny text files with report-like extensions. They exist only so the metadata scanner can see realistic extensions and folder structure. They are not valid reports, spreadsheets, images, or office documents, and the workflows must continue treating them as metadata-only inputs.

The synthetic set includes industrial, retail, office, purchase appraisal, lease-heavy, and incomplete work-in-progress assignment folders. To validate local changes without private data, run:

```powershell
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_fixtures.py
```

The smoke check scans the synthetic tree, searches the committed manifest, runs assignment discovery, builds assignment profiles, and verifies that the fixture files avoid known real-data markers. Do not point tests or smoke scripts at OneDrive paths.

For future Falcon order matching work, use the synthetic verified intelligence fixture at `tests/fixtures/synthetic_verified_intelligence/verified-intelligence.json` and the smoke check in `scripts/smoke_synthetic_intelligence_matcher.py`. See `docs/synthetic-firm-intelligence-matcher.md`.
