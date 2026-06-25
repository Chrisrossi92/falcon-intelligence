# Session Handoff

## Current Slice

The current implementation surfaces the synthetic Evidence Correction and Audit Trail foundation in the React workspace preview on top of the Subject Profile registry and Property Library work.

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
- Correction and audit models for subject fields, property fields, and candidate match fields.
- Synthetic Chad-to-Chris GBA correction showing old value, new value, reason, supporting evidence, confidence impact, and audit history.
- CLI JSON preview through `correction-audit`.
- Frontend synthetic correction data for Passport drawer field history.
- Compact Field History panel showing Correction, Prior Value, Current Value, Supporting Evidence, Confidence, approval status, and audit event history.
- Subject-profile-style field history indicator for the current subject Passport context.

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
- Persistent correction storage.
- Real uploads or source-document opening.
- Frontend persistence or write-back for corrections.

## Next Useful Slice

The next small slice should make the audit/history panel interactive while keeping the data synthetic:

- Add a read-only correction detail drill-in from the Field History panel.
- Group multiple corrections by field when more than one audit exists.
- Add rejected-correction and unapproved-correction examples to the frontend preview.
- Add appraiser note display to review actions if the correction model carries multiple notes.
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
python -m falcon_intel.cli correction-audit
```

Frontend preview checks:

```powershell
cd frontend
npx tsc -b
npx vitest run --configLoader runner
npx vite build --configLoader runner
```
