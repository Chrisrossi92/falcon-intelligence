# Session Handoff

## Current Slice

The current repository now includes the canonical Assignment Intelligence Record V1 on top of the synthetic Evidence Correction and Audit Trail foundation and controlled local historical-intake and deterministic knowledge-extraction tooling.

Added:

- Assignment Intelligence Record V1 with stable identity, schema/record versions, lineage, lifecycle, and deterministic JSON round trips.
- Adaptation from existing historical candidates and Verification Engine output without treating machine agreement as appraiser approval.
- Immutable evidence/source references, explicit appraiser/reviewer review events, current and superseded fact revisions, rejections, corrections, unresolved conflicts, and appraiser-entered facts.
- Reference-only property, ownership, comparable, market, prior-knowledge, and report-section contracts.
- Deterministic blocking/nonblocking readiness by appraisal area.
- Synthetic commercial assignment proof and focused semantic tests.

- Read-only historical intake inventory.
- Embedded/searchable PDF and DOCX candidate extraction for likely final reports and same-order DOCX companions.
- Deterministic verification, Knowledge Object candidate, and Memory Graph candidate stages.
- Privacy-safe extraction diagnostics, OCR feasibility, and an opt-in diagnostic OCR/layout pilot.

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
- Default or production OCR.
- Embeddings.
- Production ingestion or persisted real extracted facts.
- Source-document preview or retained full extracted text.
- Word report generation or export.
- Persistent registry storage.
- Persistent property library storage.
- Automatic candidate merge or comp promotion.
- Persistent correction storage.
- Real uploads or source-document opening.
- Frontend persistence or write-back for corrections.
- Production Assignment Intelligence Record persistence, live Falcon integration, or firm-specific readiness policies.
- Narrative generation, valuation conclusions, automatic comparable selection, or adjustment logic.

## Next Useful Slice

The next slice should build the smallest appraiser-reviewed assignment/property brief workflow over Assignment Intelligence Record V1. It should present assignment and subject candidates for verify/correct/reject/enter actions, recalculate readiness, and emit a reviewed brief for later report-section work without adding production persistence, real-data ingestion, report export, or narrative generation.

## Validation Notes

Run:

```powershell
$env:PYTHONPATH='src'
python -m compileall -q src scripts tests
python scripts/check_repository_safety.py
python scripts/run_smoke_suite.py
python -m pytest
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
npm ci
npm run typecheck
npm test -- --configLoader runner
npm run build -- --configLoader runner
```
