# Development Notes

## Setup

This scaffold uses Python packaging conventions but does not require third-party dependencies yet.

```powershell
python -m pip install -e .
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
$env:PYTHONPATH='src'; python scripts/smoke_cli.py
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
