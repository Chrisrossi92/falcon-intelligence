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
$env:PYTHONPATH='src'; python scripts/smoke_intelligence_card_schema.py
$env:PYTHONPATH='src'; python scripts/smoke_intelligence_card_snapshot.py
$env:PYTHONPATH='src'; python scripts/smoke_intelligence_card_cli.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_api_contract.py
$env:PYTHONPATH='src'; python scripts/smoke_match_audit.py
$env:PYTHONPATH='src'; python scripts/smoke_audit_event_snapshots.py
$env:PYTHONPATH='src'; python scripts/smoke_historical_comp.py
$env:PYTHONPATH='src'; python scripts/smoke_evidence_links.py
$env:PYTHONPATH='src'; python scripts/smoke_data_passport.py
$env:PYTHONPATH='src'; python scripts/smoke_data_passport_lookup.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_passport_contract.py
$env:PYTHONPATH='src'; python scripts/smoke_passport_detail_drawer.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_evidence_contract.py
$env:PYTHONPATH='src'; python scripts/smoke_schema_registry.py
$env:PYTHONPATH='src'; python scripts/smoke_api_envelope_snapshots.py
$env:PYTHONPATH='src'; python scripts/smoke_permission_policy.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_permission_contracts.py
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_workflow.py
$env:PYTHONPATH='src'; python scripts/smoke_cli.py
```

## Test Commands

macOS:

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
PYTHONPATH=src python3 scripts/smoke_historical_comp.py
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

Windows PowerShell:

```powershell
$env:PYTHONPATH='src'; python -m compileall -q src scripts tests
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_fixtures.py
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_intelligence_matcher.py
$env:PYTHONPATH='src'; python scripts/smoke_intelligence_card_schema.py
$env:PYTHONPATH='src'; python scripts/smoke_intelligence_card_snapshot.py
$env:PYTHONPATH='src'; python scripts/smoke_intelligence_card_cli.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_api_contract.py
$env:PYTHONPATH='src'; python scripts/smoke_match_audit.py
$env:PYTHONPATH='src'; python scripts/smoke_audit_event_snapshots.py
$env:PYTHONPATH='src'; python scripts/smoke_historical_comp.py
$env:PYTHONPATH='src'; python scripts/smoke_evidence_links.py
$env:PYTHONPATH='src'; python scripts/smoke_data_passport.py
$env:PYTHONPATH='src'; python scripts/smoke_data_passport_lookup.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_passport_contract.py
$env:PYTHONPATH='src'; python scripts/smoke_passport_detail_drawer.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_evidence_contract.py
$env:PYTHONPATH='src'; python scripts/smoke_schema_registry.py
$env:PYTHONPATH='src'; python scripts/smoke_api_envelope_snapshots.py
$env:PYTHONPATH='src'; python scripts/smoke_permission_policy.py
$env:PYTHONPATH='src'; python scripts/smoke_falcon_permission_contracts.py
$env:PYTHONPATH='src'; python scripts/smoke_synthetic_workflow.py
$env:PYTHONPATH='src'; python -m pytest
```

## Continuous Integration

GitHub Actions runs the core validation workflow on every push and pull request using Python 3.12. The workflow installs the package with development dependencies and runs:

- Python compilation for `src`, `scripts`, and `tests`.
- Synthetic fixture smoke validation.
- Synthetic intelligence matcher smoke validation.
- UI card schema, CLI, and snapshot smoke validation.
- Synthetic audit, audit event snapshots, historical comparable justification, evidence link, data passport, passport lookup, Falcon passport contract, passport drawer snapshot, Falcon evidence-open contract, schema registry, Falcon API envelope snapshots, permission policy, Falcon permission contracts, and end-to-end workflow smoke validation.
- The full pytest suite.

The CI workflow must remain synthetic-only. It must not access OneDrive, real appraisal data, report contents, OCR, embeddings, or extraction pipelines.

## Fixture Policy

Tests may use synthetic fixtures only. Do not create fixtures from real reports, client records, OneDrive exports, or extracted report text.

For a concise project checkpoint and recommended next slices, see `docs/session-handoff-roadmap.md`.

Before any real report content, extraction, OCR, embeddings, or source-document preview work, see `docs/real-data-production-readiness-gate.md`. Metadata-only real-data scans remain the only allowed real-data activity before that gate passes.

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

The versioned UI card snapshot at `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json` exists to detect accidental schema drift. Update it only when a schema change is intentional and reviewed.

Synthetic full data passport detail records live at `tests/fixtures/synthetic_data_passports/data-passports.json`. Use `scripts/smoke_data_passport_lookup.py` to validate that a Firm Intelligence card `passport_id` can resolve to a full local detail payload without source-file access.

The versioned passport detail drawer snapshot at `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json` exists to detect accidental drawer schema drift. Update it only when a drawer contract change is intentional and reviewed.

Versioned Falcon API envelope snapshots live under `tests/fixtures/synthetic_api_envelopes/`. They cover the local Falcon card response, passport detail response, and evidence-open response wrappers. Passport and evidence snapshots normalize generated audit timestamps to `synthetic-dynamic-timestamp`; do not update these snapshots unless the envelope change is intentional and reviewed.

Versioned audit event snapshots live under `tests/fixtures/synthetic_audit_events/`. They cover card viewed, passport detail opened, evidence opened, and historical comparable justification audit payloads. Generated audit timestamps are normalized to `synthetic-dynamic-timestamp`; do not update these snapshots unless the audit payload change is intentional and reviewed.
