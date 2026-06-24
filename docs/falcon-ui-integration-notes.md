# Falcon UI Integration Notes

These notes describe how Project Falcon should present Falcon Intelligence UI surfaces using the current synthetic/local contracts. This document does not authorize real data access, OneDrive access, report parsing, extraction, OCR, embeddings, or source-document preview.

## Guardrails

- No client visibility: Firm Intelligence cards, passport drawers, evidence summaries, audit metadata, internal reviewer notes, and comp/fact recommendations are internal-only.
- No automatic valuation conclusion: surfaced intelligence is assistive and must not create, imply, or select valuation conclusions without appraiser judgment.
- No real evidence opening until the production readiness gate passes: real source-document preview remains blocked by `docs/real-data-production-readiness-gate.md`.
- Metadata-only real-data scans remain the only allowed real-data activity before the gate passes.
- Appraiser remains responsible for relevance, verification, adjustments, and final report conclusions.

## Placement

### Order Detail

Place the Firm Intelligence Found card in the internal Order Detail view near the order summary and assignment context. It should appear after the order has enough seed fields to make a meaningful request:

- `tenant_id`
- `order_id`
- address, city, and state
- property type
- building size when available
- client

Order Detail should be the first Falcon UI integration target because it has stable order context and is naturally internal-facing.

### New Order Intake

Show the card as a preview panel after required seed fields are entered. The card should be quiet and non-blocking during intake:

- Do not interrupt order creation.
- Do not require users to act on matches.
- Refresh only after meaningful seed-field changes.
- Hide or collapse the card when required fields are incomplete.

### Assignment Workspace

Show the card and passport drawer in the internal assignment workspace where appraisers and reviewers can evaluate relevance. This placement can support:

- reviewing prior assignments
- opening passport details
- evaluating sale or lease comps
- writing historical comp justification
- selecting facts for later report consideration

The workspace must preserve the assistive nature of intelligence and keep report conclusions user-driven.

## Loading State

When Falcon requests a card:

- Show a compact loading state labeled around internal firm intelligence.
- Keep the rest of the order/workspace usable.
- Avoid skeletons that imply final match counts.
- If loading fails, show a quiet internal unavailable state rather than blocking the workflow.

Suggested behavior:

- `loading`: card shell with spinner or inline progress.
- `service_unavailable`: hidden card or compact unavailable message.
- `missing_required_input`: no card until seed fields are complete.

## Empty or No Intelligence State

If the contract returns no matches or the card has no meaningful top matches:

- Do not show a large empty marketing-style panel.
- Prefer a small internal note or no card.
- Continue normal appraisal workflow.
- Do not imply that no firm knowledge exists; only state that no synthetic/eligible matches were surfaced for this request.

## Permission Denied State

If role or tenant policy denies access:

- Hide the card from client users entirely.
- For internal denied users, show a minimal unavailable state only if helpful for support.
- Do not reveal match counts, passport IDs, evidence IDs, source document metadata, or reason details that expose internal intelligence.
- Create or forward a denied-access audit event when production audit policy requires it.

Current local permission scaffolding is in `src/falcon_intel/permission_policy.py`; it is not production auth.

## Passport Detail Drawer States

The passport detail drawer opens from a top match `passport_id`. Current synthetic UI contract:

```text
tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json
```

Recommended states:

- `closed`: no detail requested.
- `loading`: drawer shell opens with loading indicator after user selects a passport.
- `ready`: show passport identity, fact summary, verification/review summary, confidence dimensions, evidence link summaries, audit event IDs, searchable status, and warnings.
- `not_found`: show a quiet unavailable state and keep the card visible.
- `permission_denied`: close or replace contents with a minimal access message; do not expose passport fields.
- `error`: show a retry-safe internal error state.

The drawer should not contain raw report text, extracted source content, absolute paths, or real document previews.

## Evidence States

Evidence rows inside the passport drawer are metadata summaries. Selecting an evidence row calls the synthetic evidence-open contract in local tests.

Recommended states:

- `metadata_placeholder`: show evidence label, source document type, access level, and placeholder status.
- `disabled`: show disabled state and do not call a real viewer.
- `not_found`: evidence ID is no longer attached to the passport; show unavailable state.
- `permission_denied`: show minimal access denied state.
- `preview_blocked`: real source preview is blocked until the production readiness gate passes.

Evidence unavailable or disabled states must not expose source content or real paths.

## Historical Comp Justification Modal

Use the historical comp justification modal when a user selects a stale or historical comparable for consideration.

The modal should include:

- selected comp identifier
- comp date or age
- stale/historical warning
- reason code options
- optional custom explanation
- generated reusable narrative preview
- suggested audit payload

The modal should make clear:

- justification is required for historical comp use
- narrative text is draft support, not a final report conclusion
- appraiser remains responsible for use and wording

## Audit Handoff

Falcon Intelligence local contracts return suggested audit payloads. Falcon production must persist audit events through its own durable audit service.

Audit handoff expectations:

- Card viewed: emitted when the Firm Intelligence Found card is shown or intentionally opened.
- Passport/detail opened: emitted when the user opens a passport detail drawer.
- Evidence opened: emitted when the user selects an evidence row.
- Historical comp justification written: emitted when the user saves justification text.
- Match selected/rejected: emitted when the user acts on a match.

Suggested audit payloads should be treated as inputs to Falcon audit persistence, not as completed audit records. Production audit must add any required actor role, company context, request ID, IP/session metadata, result status, and persistence timestamp.

## Recommended First Falcon UI Slice

Start with an internal-only Order Detail card preview using synthetic/local contract data.

Scope:

- Render the Firm Intelligence Found card from the v1 snapshot shape.
- Support loading, unavailable, missing-input, and permission-denied states.
- Show grouped match counts and top match summaries.
- Add a disabled or placeholder action for opening passport detail.
- Do not open real evidence.
- Do not connect to real report content.
- Do not show the card to client users.

After that, add the passport detail drawer using the v1 drawer snapshot, then connect the synthetic evidence-open unavailable/placeholder state.

## Current Contract References

- Card schema snapshot: `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json`
- Passport drawer snapshot: `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json`
- Synthetic end-to-end workflow: `scripts/smoke_synthetic_workflow.py`
- Falcon card contract: `src/falcon_intel/falcon_api_contract.py`
- Falcon passport contract: `src/falcon_intel/falcon_passport_contract.py`
- Falcon evidence-open contract: `src/falcon_intel/falcon_evidence_contract.py`
- Permission scaffold: `src/falcon_intel/permission_policy.py`
- Production readiness gate: `docs/real-data-production-readiness-gate.md`
