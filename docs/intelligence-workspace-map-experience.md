# Falcon Intelligence Workspace / Map Experience

This document is the first real UX specification for the Falcon Intelligence Workspace, centered on the Map experience. It is documentation-only. It does not authorize backend architecture, real data access, OneDrive access, extraction, OCR, embeddings, source-document preview, production database/auth, or production map provider integration.

The assumed UI data source remains the existing synthetic contracts and snapshots, especially `map_workspace_response`, assignment profiles, firm intelligence card summaries, data passports, evidence links, audit events, permission decisions, and schema registry entries.

## Product Positioning

Falcon Core manages work. It owns orders, assignments, calendars, clients, operational status, delivery, users, roles, and client-facing workflows.

Falcon Intelligence remembers institutional knowledge. It turns completed appraisal work into verified, internal, tenant-scoped knowledge that can help appraisers and reviewers understand what the firm already knows about properties, markets, comparables, prior assignments, and supporting evidence.

Falcon Intelligence is a premium module inside the Falcon platform. It should feel like a natural extension of Falcon Core, not a separate app with a different visual or behavioral language. The appraiser always remains responsible. AI can assist, summarize eligible metadata, suggest workflow routes, and surface relevant records, but it must never silently conclude, select comps, or replace professional judgment.

North Star:

> Falcon Intelligence transforms every completed appraisal into verified institutional knowledge that makes every future appraisal faster, more informed, and more defensible.

## Falcon Shell Placement

The future Falcon shell should keep Intelligence as a first-class premium module in the same operating environment as Core:

```text
Dashboard
Orders
Calendar
Clients

Intelligence

Administration
```

Inside Intelligence, the recommended module navigation is:

```text
Overview
Map
Subjects
Sales
Leases
Reports
Market
```

Map is the primary Intelligence workspace. Overview can summarize module health, recent verified knowledge, stale warnings, and reviewer queues, but Map is where users orient spatially, inspect records, and open provenance.

## Core Questions

Every Intelligence surface should answer one of four questions:

| Question | Primary surface | UX role |
| --- | --- | --- |
| Where is it? | Map | Spatial orientation, clustering, filters, nearby records, market context. |
| What do we know? | Passport | Verified facts, status, confidence, freshness, and searchability. |
| Why do we believe it? | Evidence | Source metadata, evidence summaries, support count, access state, and limitations. |
| Who verified it? | Audit | Verifier, reviewer, timestamps, decisions, changes, and accountability trail. |

These questions should be visible in the product structure. The workspace should not feel like a generic AI dashboard or analytics page.

## Intelligence Hierarchy

Use this hierarchy as the mental model for navigation, disclosure, and auditability:

```text
Firm
-> Market
-> Property
-> Passport
-> Fact
-> Evidence
-> Audit
```

Implications:

- Firm context defines tenant boundaries, module access, and policy.
- Market context helps explain relevance, geography, property type, and comparable clusters.
- Property is the core object users orient around on the map.
- Passport is the trust container for a property, comp, assignment, or fact.
- Fact is the reviewed unit of knowledge.
- Evidence explains why the fact is supportable.
- Audit explains who acted, when, and under what decision path.

## Canonical Map Workspace Layout

The Map workspace should be a dense, low-scroll professional workspace. It should prioritize orientation, traceability, and fast inspection over decorative panels.

```text
+--------------------------------------------------------------------------------+
| Falcon shell / Intelligence navigation                                          |
+--------------+-----------------------------------------------------------------+
| Filter rail  | Large interactive map canvas                                    |
|              |                                                                 |
|              |                                                                 |
|              |                                                                 |
|              |                                                                 |
+--------------+-----------------------------------------------------------------+
| Synchronized assignments / intelligence table                                  |
+--------------------------------------------------------------------------------+
                                      +-------------------------------------------+
                                      | Passport detail drawer                    |
                                      |  + nested Evidence drawer                 |
                                      |  + nested Audit history drawer            |
                                      +-------------------------------------------+
```

### Left: Filter Rail

The filter rail is the user's control surface. It should be compact, persistent, and optimized for professional filtering rather than broad dashboard browsing.

Initial filters should reflect the existing `map_workspace_response` contract:

- Property type.
- Record type.
- Status.
- Verification status.
- Stale flag.
- City.
- State.

Future filters may include market, submarket, effective date, report date, verifier, reviewer, client, confidence dimension, evidence availability, and permission level only after contract support is intentionally added.

### Center/Right: Map Canvas

The map canvas is the primary workspace surface. It answers "Where is it?" and should occupy most of the first viewport.

Expected behavior:

- Show records from the current filtered result set.
- Use marker states for selected, stale, verified, suggested, permission-limited, and disabled records.
- Keep clustering and density controls calm and utilitarian.
- Avoid novelty map styling, animated AI effects, or overbearing confidence colors.
- Treat map provider integration as future work. The current specification only assumes synthetic coordinates from the existing map workspace snapshot.

### Bottom: Synchronized Table

The bottom table is the structured review surface for the same result set shown on the map. It should be scrollable without moving the whole page.

Initial row content should map to existing synthetic record fields:

- Display label.
- Record type.
- Address/city/state.
- Property type.
- Status.
- Verification status.
- Confidence summary.
- Evidence link count.
- Stale flag.
- Passport availability.

The table should support professional scanning, keyboard-friendly selection, and stable row height. It should not become a wall of cards.

### Right: Passport Detail Drawer

The passport drawer opens over the workspace and preserves map/table context. It answers "What do we know?"

The drawer should use the existing `passport_detail_drawer` contract and show:

- Passport identity.
- Fact summary.
- Verification and review summary.
- Confidence dimensions.
- Evidence summaries.
- Audit event IDs or summary links.
- Searchable status.
- Warnings.

The drawer must not include real source text, raw report content, absolute paths, OneDrive paths, or source-document previews.

### Nested Drawers: Evidence and Audit

Evidence and audit should open as secondary disclosure from the passport drawer, not as full-page navigation.

Evidence answers "Why do we believe it?" and should use the existing evidence link and evidence-open response contracts. It remains metadata-only in the current milestone.

Audit answers "Who verified it?" and should use the existing audit event model and audit event envelope snapshots. Production persistence remains future Falcon responsibility.

Closing nested drawers should return the user to the passport drawer. Closing the passport drawer should return the user to the same map bounds, filters, table scroll position, and selected record.

## Interaction Model

Map, table, passport, evidence, and audit must stay synchronized without stealing context.

| User action | Expected behavior |
| --- | --- |
| Change a filter in the rail | Table rows and map markers update together. Selection is preserved only if the selected record remains in the filtered set. |
| Click a map marker | Matching table row highlights, scrolls into view if needed, and the marker enters selected state. |
| Click a table row | Matching map marker highlights and the map may pan or zoom enough to make the marker visible. |
| Click a property, row action, or passport affordance | Passport drawer opens for the selected record when `passport_id` is available and permitted. |
| Select evidence from passport | Evidence drawer opens with metadata-only evidence summary and permission-aware disabled/unavailable states. |
| Select audit from passport or evidence | Audit drawer opens with relevant event timeline or placeholder metadata. |
| Close audit drawer | User returns to the evidence or passport context that opened it. |
| Close evidence drawer | User returns to passport context. |
| Close passport drawer | User returns to unchanged map/table/filter context. |

Empty, denied, and unavailable states should be quiet. They should not reveal sensitive match counts, evidence IDs, source metadata, or reason detail to roles that lack access.

## Existing Synthetic Contract Mapping

Do not invent new schemas for this milestone. UI surfaces should consume existing contracts and snapshots as follows:

| Existing contract/model | Current source | UI surface |
| --- | --- | --- |
| Map Workspace Contract | `docs/intelligence-map-workspace-contract.md`; `tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json` | Map canvas, synchronized bottom table, filter rail, selected record state, result counts. |
| Assignment Profiles | `docs/assignment-profiles.md`; synthetic assignment profile fixtures | Marker and table row context for discovered or completed assignments. |
| Firm Intelligence Found Card | `docs/falcon-integration-contract.md`; `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json` | Workspace summary, selection summary, and future cross-entry from Order Detail or Assignment workspace. |
| Passport Model / Passport Drawer | `docs/data-confidence-provenance-model.md`; `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json` | Right-side passport drawer. |
| Evidence Link Model / Evidence Open Contract | `docs/data-confidence-provenance-model.md`; `tests/fixtures/synthetic_api_envelopes/falcon-evidence-open-api-response-v1.json` | Evidence section and nested evidence drawer. |
| Audit Event Model / Audit Event Envelope | `docs/verified-intelligence-workflow.md`; `tests/fixtures/synthetic_audit_events/` | Audit history drawer and suggested audit handoff. |
| Permission Policy | `docs/falcon-ui-integration-notes.md`; `src/falcon_intel/permission_policy.py` | Hidden, disabled, unavailable, and permission-denied UI states. |
| Schema Registry and Changelog | `docs/schema-version-registry.md`; `docs/schema-changelog.md` | Future UI contract governance and deliberate snapshot review. |

## Visual And Brand Principles

Falcon Intelligence should inherit the Falcon shell feel:

- Professional appraisal platform.
- Calm, clean, operational.
- Premium but not flashy.
- Minimal scrolling.
- Drawers over full-page navigation.
- Progressive disclosure.
- Trust, traceability, and reviewer accountability as the brand.

Visual guidance:

- Use restrained dark/light neutral palettes as Falcon supports them.
- Prefer clear workspace labels and precise status language.
- Avoid gimmicky AI gradients, glowing confidence graphics, and novelty visual effects.
- Avoid over-carded dashboards and marketing-style sections.
- Use dense professional data where needed, but disclose detail progressively through drawers.
- Show confidence, verification, stale, and permission states clearly without overpowering appraiser judgment.
- Treat "AI Suggestions" as a future layer that is visually subordinate to verified knowledge.
- Do not imply that the system has concluded value, relevance, or comp selection.

## Workspace Layers

The Map workspace should eventually support layers, but implementation is future work and must follow contract and gate review.

Future layers:

- Subjects.
- Sales.
- Leases.
- Reports.
- Verified Knowledge.
- AI Suggestions.
- Reviewer Flags.
- Market Areas.
- Comparable Clusters.

Layer rules:

- Verified Knowledge should be more visually authoritative than AI Suggestions.
- Reviewer Flags should be visible enough to prevent misuse but not presented as punitive decoration.
- Market Areas and Comparable Clusters should support context, not automatic conclusion.
- Layers that require real location data, production map providers, source documents, extraction, or embeddings remain blocked until the relevant production gates pass.

## Permission And Accountability Behavior

Permission states are part of the workspace, not an afterthought.

Expected states:

- Client users: Intelligence hidden entirely.
- Internal denied users: minimal unavailable state, no sensitive counts or IDs.
- Trainee users: limited visibility consistent with the current permission scaffold.
- Evidence disabled: show metadata-safe disabled state and do not open a viewer.
- Passport unavailable: keep map/table context and show a quiet drawer state.
- Audit unavailable: show an unavailable timeline state without blocking workspace navigation.

Every future production action that opens, selects, rejects, verifies, or reuses intelligence should generate an audit event through Falcon's durable audit system. Current contracts only return suggested audit payloads.

## V2A Documentation Slice

This document starts the V2 Intelligence Workspace product definition track. It does not supersede the existing synthetic contract roadmap. Instead, it translates existing V1/V5-style contract work into the first canonical workspace experience.

V2A is complete when:

- The Map workspace UX model is documented.
- Existing synthetic contracts are mapped to UI surfaces.
- Product positioning inside Falcon is explicit.
- Non-goals and production gates remain intact.
- No React UI, backend architecture, production auth, real extraction, OCR, embeddings, source preview, OneDrive access, or production database work is added.

Recommended next slices:

1. V2B: Workspace state inventory for empty, loading, permission denied, stale, no-results, and evidence-unavailable states.
2. V2C: Low-fidelity layout checklist for Falcon shell integration, still documentation-only or static mock only.
3. V2D: Contract gap review, limited to identifying whether existing v1 snapshots can support a first React preview without schema changes.
4. V2E: Internal-only React preview against existing synthetic snapshots after UX approval.

## Non-Goals

This milestone does not include:

- React UI implementation.
- Production API design.
- Database schema design.
- Real extraction.
- OCR.
- Embeddings.
- Source-document preview.
- OneDrive access.
- Google Maps or other production map provider integration.
- Real report data.
- Client-visible Intelligence surfaces.
- Automatic valuation conclusions, comp selection, narrative generation, or report language.

