# Schema Changelog

Falcon Intelligence schema changes must be deliberate, reviewable, and synthetic-only until the production readiness gates approve broader work. This changelog records contract changes for UI-facing and Falcon-style API/RPC schemas.

This document does not authorize real appraisal data, OneDrive access, report parsing, extraction, OCR, embeddings, source-document preview, or production API behavior.

## Change Template

Use this template before changing a versioned schema or overwriting a snapshot fixture.

### Schema Name

`schema_name`

### Current Version

`1`

### Proposed Version

`1` for additive backward-compatible changes, or the next integer for breaking changes.

### Reason For Change

Explain the product or integration need. Link the slice, issue, or approval note when available.

### Breaking Vs Additive

- Breaking: removed required field, renamed field, changed field type, changed field meaning, changed enum/code semantics, or requires consumer code changes.
- Additive: optional field or optional metadata that existing consumers can ignore without behavior changes.

### Affected Snapshots

List every committed snapshot path that must be reviewed or regenerated.

### Affected Consumers

List known consumers such as Falcon Order Detail, New Order intake, Assignment workspace, passport drawer, evidence workflow, audit persistence, or map workspace.

### Migration Notes

Describe consumer changes, fallback behavior, version detection, or compatibility assumptions.

### Approval Checklist

- [ ] `AGENT_GUIDE.md` reviewed.
- [ ] `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md` reviewed.
- [ ] Change remains synthetic/local unless a production gate explicitly allows otherwise.
- [ ] No real data, OneDrive access, extraction, OCR, embeddings, source-document preview, or source files are introduced.
- [ ] Schema registry entry and constants are updated if the version changes.
- [ ] Snapshot diff is reviewed deliberately.
- [ ] Regression tests and smoke validation are updated.
- [ ] Affected docs are updated.

## Current V1 Baseline Entries

### Firm Intelligence Found Card

- Schema name: `firm_intelligence_found_card`
- Current version: `1`
- Snapshot: `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json`
- Consumers: Falcon internal Order Detail, New Order intake, and Assignment workspace UI.
- Baseline note: v1 is the synthetic UI card contract for grouped matches, top match cards, confidence/provenance summary, warnings, and recommended actions.
- Change rule: changes to required card fields, match group semantics, top-match identity fields, or provenance summary semantics require deliberate snapshot review and may require a new version.

### Passport Detail Drawer

- Schema name: `passport_detail_drawer`
- Current version: `1`
- Snapshot: `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json`
- Consumers: Falcon internal passport detail drawer.
- Baseline note: v1 is the synthetic drawer contract for fact identity, verification/review summary, confidence dimensions, evidence link summaries, audit event ids, searchable status, and warnings.
- Change rule: changes to fact identity, confidence dimension meaning, evidence summary shape, or verification/review semantics require deliberate snapshot review and may require a new version.

### Falcon API Envelopes

- Schema names: `falcon_card_api_response`, `falcon_passport_detail_api_response`, `falcon_evidence_open_response`
- Current version: `1`
- Snapshots:
  - `tests/fixtures/synthetic_api_envelopes/falcon-card-api-response-v1.json`
  - `tests/fixtures/synthetic_api_envelopes/falcon-passport-detail-api-response-v1.json`
  - `tests/fixtures/synthetic_api_envelopes/falcon-evidence-open-api-response-v1.json`
- Consumers: future Falcon API/RPC clients for card retrieval, passport detail lookup, evidence metadata, permission-denied responses, and audit handoff.
- Baseline note: v1 envelope snapshots lock top-level `schema_version`, `status`, payload object placement, safe error shape, and suggested audit payload shape where present.
- Change rule: changes to envelope status codes, top-level payload keys, permission-denied shape, or suggested audit payload placement require deliberate snapshot review and may require a new version.

### Audit Event Envelope

- Schema name: `audit_event_envelope`
- Current version: `1`
- Snapshot directory: `tests/fixtures/synthetic_audit_events/`
- Consumers: future Falcon audit persistence and internal compliance handoff.
- Baseline note: v1 audit snapshots lock synthetic audit payloads for card viewed, passport detail opened, evidence opened, and historical comparable justification events. Dynamic timestamps are normalized for deterministic regression tests.
- Change rule: changes to event codes, required audit identity fields, timestamp semantics, or metadata placement require deliberate snapshot review and may require a new version.

### Map Workspace Response

- Schema name: `map_workspace_response`
- Current version: `1`
- Snapshot: `tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json`
- Consumers: future Falcon internal Intelligence Map Workspace page.
- Baseline note: v1 is the synthetic table/map contract for `table_rows`, `map_pins`, `selected_record`, `result_counts`, and `available_filters`.
- Change rule: changes to row/pin identity, selected-record sync behavior, coordinate semantics, filter keys, or result count semantics require deliberate snapshot review and may require a new version.

## Maintenance Rules

- Keep this changelog aligned with `docs/schema-version-registry.md`.
- Add a changelog entry before changing a snapshot fixture.
- Do not overwrite snapshots as incidental cleanup.
- Prefer additive v1 changes only when existing Falcon consumers can ignore the new field safely.
- Use a new version for breaking changes, and keep old snapshots available until downstream consumers migrate or explicitly drop support.
