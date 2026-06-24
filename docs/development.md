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
```

## Fixture Policy

Tests may use synthetic fixtures only. Do not create fixtures from real reports, client records, OneDrive exports, or extracted report text.
