# Falcon Integration Contract

This document defines how Project Falcon should consume Falcon Intelligence for the future "Firm Intelligence Found" card. It is documentation-only. It does not authorize real data access, OneDrive access, report parsing, extraction, OCR, embeddings, or ingestion.

## Status

Current implementation is synthetic-only. The stable UI schema is exercised by the committed snapshot:

```text
tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json
```

Falcon production integration must not treat the synthetic matcher as a production data service until a separate approved API, tenant isolation, permission model, audit logging, and verified-intelligence backend exist.

The repository includes a local in-memory contract helper, `build_falcon_intelligence_card_response`, for tests only. It is not a web server, Supabase RPC, database service, or production API.

## Falcon Placement

Falcon may surface the card in three internal-only locations:

- Order Detail: show after an order has enough seed fields to match against verified firm intelligence.
- New Order intake: preview possible firm intelligence while an internal user enters or reviews order details.
- Assignment workspace: show relevant verified intelligence while the assigned appraiser or reviewer works the assignment.

The card must not be visible in client-facing views, shared portals, external deliverables, or unauthenticated contexts.

See `docs/falcon-ui-integration-notes.md` for recommended UI states, placement details, permission-denied handling, evidence unavailable behavior, and audit handoff guidance.

## Request Inputs

Falcon sends a structured order seed. Required fields:

```json
{
  "order_id": "falcon-order-synthetic-001",
  "tenant_id": "tenant-synthetic-001",
  "company_id": "company-synthetic-001",
  "address": "1000 Example Industrial Way",
  "property_type": "industrial",
  "building_size_sf": 50000,
  "client": "Synthetic Lender A",
  "borrower_contact": "Synthetic Borrower Contact"
}
```

Field notes:

- `order_id`: Falcon order identifier for audit and UI correlation.
- `tenant_id` / `company_id`: required for tenant isolation and permission checks.
- `address`: order seed address. Future production matching should normalize address fields before matching.
- `property_type`: high-level property type used for routing signals.
- `building_size_sf`: numeric building size in square feet.
- `client`: internal order client or ordering party name as permitted by tenant policy.
- `borrower_contact`: optional borrower/contact context. It must remain internal-only unless explicitly shared by firm policy.

## Response Schema

Falcon receives the UI-facing card schema produced by `build_firm_intelligence_card`. The current synthetic reference is:

```text
tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json
```

Required top-level fields:

- `schema_version`
- `headline`
- `order_summary`
- `match_group_summaries`
- `top_match_cards`
- `confidence_provenance_summary`
- `warnings`
- `recommended_actions`

Schema versioning rules:

- `schema_version` is required on every response.
- Backward-compatible additions may keep the same major version when existing fields retain meaning and type.
- Field removals, renames, type changes, or semantic changes require a new schema version.
- Snapshot updates must be deliberate: update docs, regenerate `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json` or add a new versioned snapshot, and review the JSON diff.
- Falcon should reject unknown major schema versions until the frontend has been updated to support them.

## Permission Boundaries

The card is internal-only.

Rules:

- Client users must not see the card.
- Internal visibility must be role-scoped to owners, admins, appraisers, and reviewers according to Falcon policy.
- Every request must include tenant/company context.
- Falcon Intelligence must return only tenant-scoped records.
- No cross-tenant or cross-company intelligence mixing is allowed.
- Supporting evidence links must be permission-limited and must not expose source documents or report contents unless a future approved workflow permits it.

Current local permission scaffold:

- Module: `src/falcon_intel/permission_policy.py`
- Test: `tests/test_permission_policy.py`
- Smoke script: `scripts/smoke_permission_policy.py`

The scaffold defines role codes for `owner`, `admin`, `appraiser`, `reviewer`, `trainee`, and `client`. It returns decision objects with `allowed`, `reason_code`, and `reason_label` for card visibility, passport detail visibility, evidence link opening, fact verification, fact review, fact override, and fact archive actions.

This scaffold is not production auth. Falcon production integration must enforce tenant membership, order access, user roles, source-document permissions, and durable audit logging outside this local policy helper.

## Future API/RPC Boundary

The production boundary can be implemented as an internal API or Supabase RPC. The boundary should be narrow and auditable.

Current local contract test boundary:

- Module: `src/falcon_intel/falcon_api_contract.py`
- Function: `build_falcon_intelligence_card_response`
- Test: `tests/test_falcon_api_contract.py`
- Smoke script: `scripts/smoke_falcon_api_contract.py`

This boundary runs in memory and uses only committed synthetic verified intelligence fixtures. It does not start a web server, open network ports, query a database, access OneDrive, or read report contents.

Request shape:

```json
{
  "request_id": "req-synthetic-001",
  "actor": {
    "user_id": "user-synthetic-001",
    "role": "appraiser"
  },
  "order": {
    "order_id": "falcon-order-synthetic-001",
    "tenant_id": "tenant-synthetic-001",
    "company_id": "company-synthetic-001",
    "address": "1000 Example Industrial Way",
    "property_type": "industrial",
    "building_size_sf": 50000,
    "client": "Synthetic Lender A",
    "borrower_contact": "Synthetic Borrower Contact"
  }
}
```

Response shape:

```json
{
  "request_id": "req-synthetic-001",
  "status": "ok",
  "card": {
    "schema_version": "1",
    "headline": "Firm Intelligence Found: 17 synthetic matches across 8 groups."
  }
}
```

Passport detail local contract boundary:

- Module: `src/falcon_intel/falcon_passport_contract.py`
- Function: `build_falcon_passport_detail_response`
- Test: `tests/test_falcon_passport_contract.py`
- Smoke script: `scripts/smoke_falcon_passport_contract.py`

This boundary resolves a card `passport_id` to full synthetic data passport detail for a future internal detail drawer. It runs in memory and uses only `tests/fixtures/synthetic_data_passports/data-passports.json`.

Passport detail request shape:

```json
{
  "tenant_id": "tenant-synthetic-001",
  "order_id": "falcon-order-synthetic-001",
  "user_id": "user-synthetic-001",
  "passport_id": "synthetic-passport-assignment-industrial-alpha"
}
```

Passport detail response shape:

```json
{
  "status": "ok",
  "tenant_id": "tenant-synthetic-001",
  "order_id": "falcon-order-synthetic-001",
  "user_id": "user-synthetic-001",
  "passport_id": "synthetic-passport-assignment-industrial-alpha",
  "passport": {
    "passport_id": "synthetic-passport-assignment-industrial-alpha",
    "verification_status": "verified",
    "evidence_links": []
  },
  "suggested_audit_event": {
    "event_code": "opened_evidence"
  }
}
```

Passport detail statuses:

| Status | Meaning | Expected Falcon behavior |
| --- | --- | --- |
| `ok` | Passport detail was found for the tenant and passport ID. | Show the internal detail drawer and persist the suggested audit event through Falcon's audit service. |
| `not_found` | Passport ID is missing, unknown, or does not belong to the tenant. | Do not show detail; keep card visible and show a quiet internal unavailable state. |
| `missing_required_input` | Required detail request fields are missing. | Do not call the detail drawer; log local integration issue during development. |

Passport detail drawer UI contract:

- Serializer: `build_passport_detail_drawer`
- Snapshot: `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json`
- Test: `tests/test_passport_detail_drawer.py`
- Smoke script: `scripts/smoke_passport_detail_drawer.py`

The drawer contract is a UI-facing projection of full passport detail. It shows summary evidence rows and warning states, but it does not open source documents, read report contents, or expose extraction output.

Evidence-open local contract boundary:

- Module: `src/falcon_intel/falcon_evidence_contract.py`
- Function: `build_falcon_evidence_open_response`
- Test: `tests/test_falcon_evidence_contract.py`
- Smoke script: `scripts/smoke_falcon_evidence_contract.py`

This boundary validates that a selected `evidence_id` belongs to the requested synthetic `passport_id`, returns a safe evidence summary, and suggests an `opened_evidence` audit event. It does not open files, read report contents, query OneDrive, run extraction, or return source text.

Evidence-open request shape:

```json
{
  "tenant_id": "tenant-synthetic-001",
  "order_id": "falcon-order-synthetic-001",
  "user_id": "user-synthetic-001",
  "passport_id": "synthetic-passport-assignment-industrial-alpha",
  "evidence_id": "synthetic-evidence-assignment-industrial-alpha"
}
```

Evidence-open statuses:

| Status | Meaning | Expected Falcon behavior |
| --- | --- | --- |
| `ok` | Evidence belongs to the passport and summary is safe to show. | Show metadata-only evidence unavailable/placeholder state and persist suggested audit event. |
| `not_found` | Passport is unknown or outside tenant scope. | Do not show evidence detail. |
| `evidence_not_found` | Evidence ID is not attached to the passport. | Keep drawer open and show a quiet unavailable state. |
| `missing_required_input` | Required request fields are missing. | Do not attempt evidence open; log local integration issue during development. |

End-to-end synthetic workflow:

- Module: `src/falcon_intel/synthetic_workflow.py`
- Function: `run_synthetic_intelligence_workflow`
- Test: `tests/test_synthetic_workflow.py`
- Smoke script: `scripts/smoke_synthetic_workflow.py`

This workflow proves the local trust path: Falcon-style order payload, Firm Intelligence card, top-match passport ID, passport detail contract, permission decisions, evidence-open contract, and suggested audit payloads for card viewed, passport detail opened, and evidence opened. It is synthetic-only and does not persist audit events.

Error states:

| Status | Meaning | Expected Falcon behavior |
| --- | --- | --- |
| `missing_required_input` | Required order seed fields are missing or invalid. | Hide the card and prompt internal user to complete order fields. |
| `permission_denied` | Actor role or tenant context cannot view internal intelligence. | Hide the card and log denied access. |
| `tenant_mismatch` | Request tenant/company does not match available intelligence scope. | Hide the card and alert internal support/admin flow. |
| `schema_version_unsupported` | Falcon does not support the returned card schema version. | Hide the card and surface internal integration warning. |
| `service_unavailable` | Matching service cannot respond. | Continue Falcon workflow without intelligence card. |
| `no_matches` | Request succeeded but no verified intelligence was found. | Show no card or a quiet internal empty state, depending on UI policy. |

## Audit Requirements

Falcon must create audit events for card and evidence interactions.

Audit when:

- Card is viewed.
- User expands a match group.
- User opens supporting evidence or provenance details.
- User copies, selects, links, or uses a recommended comp.
- User copies, selects, links, or uses a recommended fact or market indicator.
- User dismisses or rejects a surfaced match.
- User overrides stale-data warnings or policy warnings.

Minimum audit event fields:

- `tenant_id`
- `company_id`
- `order_id`
- `actor_user_id`
- `actor_role`
- `event_type`
- `schema_version`
- `match_source_id`, when applicable
- `match_source_type`, when applicable
- `timestamp`
- `result`
- `justification`, when policy requires it

Audit logs should be append-only. Reuse of a comp or fact should preserve source provenance and create a new event rather than rewriting prior history.

## Guardrails

The card is assistive.

Required guardrails:

- Intelligence is a recommendation surface, not a conclusion engine.
- The appraiser remains responsible for relevance, selection, adjustment, and final conclusions.
- No automatic report conclusions may be generated from card output.
- No automatic comparable selection may occur without user action.
- All surfaced facts must be traceable to verified records and provenance.
- Stale data must be visible before reuse.
- Rejected intelligence must not appear in normal card output.
- Clients must not see internal firm intelligence.
- Production matching must not use real report contents unless a future extraction and permission gate is approved.

## Current Implementation Boundary

Current repository support is limited to synthetic fixtures, metadata-only scanners, synthetic matcher output, a UI-facing synthetic card schema, and versioned synthetic card snapshots. No real Falcon production data, OneDrive data, report contents, extraction, OCR, embeddings, or source-document reads are part of this contract.

See `docs/intelligence-match-policy.md` for match scoring, ranking, warning, action prompt, and audit policy.
