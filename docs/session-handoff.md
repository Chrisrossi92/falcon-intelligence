# Session Handoff

## Current Slice

The current repository now includes the complete synthetic Local Intake Review to Assignment/Property Brief V1 workflow over the canonical Assignment Intelligence Record V1, on top of controlled local historical-intake and deterministic knowledge-extraction tooling.

Added:

- AIR-backed Local Intake Review application service with practical appraisal-topic grouping.
- Accept, additive correction, retained rejection, defer, explicit conflict resolution, and appraiser-entered fact operations using canonical AIR review semantics.
- Deterministic readiness recalculation with missing-critical, unresolved-conflict, unverified-material, weak/stale-evidence, and deferred-review issues.
- Assignment/Property Brief V1 with assignment/subject synopses, issues, evidence citations, reference-only comparable/market leads, readiness, and explicit professional boundaries.
- Guarded AIR JSON, brief JSON, and Markdown exports restricted to approved ignored or out-of-repository paths.
- Backend-generated versioned React workspace projection and focused intake UI with filters, needs-attention views, next-unreviewed navigation, provenance, actions, blockers, brief review, and export controls.
- Twenty-candidate code-only synthetic Northstar proof with one resolved conflict, unresolved conflicts, a missing critical field, all required decision states, deterministic rebuilds, and round-trip tests.

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
- Production frontend persistence or backend write-back; additional React preview interactions remain in memory over the backend-generated synthetic projection.
- Production Assignment Intelligence Record persistence, live Falcon integration, or firm-specific readiness policies.
- Narrative generation, valuation conclusions, automatic comparable selection, or adjustment logic.

## Next Useful Action

After review, merge this branch, synchronize the work-computer checkout, and conduct one tightly controlled local pilot using one deliberately selected real assignment stored outside the repository. Keep extraction/review/brief outputs ignored and local, record accuracy and timing without confidential text in Git, confirm the brief helps start the report, inspect Git status for leakage, and stop before narrative or valuation automation. See `docs/local-intake-review-workflow.md`.

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
python -m falcon_intel.cli local-intake-review
python -m falcon_intel.cli local-intake-review --export-dir data\local-intake-review\synthetic-northstar
```

Frontend preview checks:

```powershell
cd frontend
npm ci
npm run typecheck
npm test -- --configLoader runner
npm run build -- --configLoader runner
```
