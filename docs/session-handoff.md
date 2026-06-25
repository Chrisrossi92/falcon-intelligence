# Session Handoff

## Current Slice

The current implementation adds the synthetic Property Library / Controlled Comp Vault foundation on top of the Subject Profile registry work.

Added:

- Report Field Registry types and lifecycle helpers.
- Synthetic Subject Profile for `517 E Riverview Avenue`.
- CLI JSON preview through `subject-profile`.
- Appraiser workflow simulation for `--approve` and `--lock`.
- Readiness metrics for completion and report merge readiness.
- Documentation for the registry architecture and guardrails.
- Property Library types for canonical properties, evidence events, report usages, and candidate normalization matches.
- Synthetic map-first workspace preview through `property-library`.
- Filters for property type, county, comp role, report usage, date range, size range, and verification status.
- Selected property drawer with linked evidence, reports/orders, and conflicts.
- Controlled Comp Vault documentation covering property/evidence/report-usage separation.

## Current Boundary

This slice does not add:

- Real OneDrive integration.
- OCR.
- Embeddings.
- Source document extraction.
- Report body parsing.
- Word report generation or export.
- Persistent registry storage.
- Persistent property library storage.
- Automatic candidate merge or comp promotion.

## Next Useful Slice

The next small slice should add a synthetic review queue shared by Subject Profile fields and Property Library candidate matches:

- Queue missing or needs-review subject fields.
- Queue candidate normalization conflicts.
- Add appraiser notes to review actions.
- Emit an audit-style event list in memory.
- Keep all values synthetic and avoid report export.

## Validation Notes

Run:

```powershell
$env:PYTHONPATH='src'
python -m pytest
python scripts/smoke_cli.py
```

The CLI previews can be checked with:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli subject-profile
python -m falcon_intel.cli property-library
```
