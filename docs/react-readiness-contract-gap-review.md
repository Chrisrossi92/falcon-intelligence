# React Readiness and Contract Gap Review

This document defines V2D: React Readiness & Contract Gap Review for Falcon Intelligence. It is documentation-only. It does not authorize React implementation, map rendering, schema changes, contract changes, backend architecture, real extraction, OCR, embeddings, OneDrive access, source-document preview, production auth, production database, or production map provider integration.

## Purpose

This review exists to answer one question:

> Can Falcon Intelligence begin React implementation using only the current synthetic contracts?

Answer: yes. The first React implementation can begin from the current v1 synthetic contracts and documentation. The existing contracts are sufficient for a first internal Map workspace preview when the UI derives presentation state from current payloads rather than requesting new schemas.

Schema growth should remain the exception. The preferred implementation posture is:

- Reuse existing contracts.
- Derive UI state.
- Preserve snapshot compatibility.
- Add UI composition before adding schema surface.
- Defer production data, production auth, source preview, embeddings, OCR, extraction, and production map provider work.

## Inventory Of Existing Contracts

The current contract surface is intentionally ahead of UI implementation. These assets should not be modified for the first React workspace slice.

| Contract or asset | Current support for UI |
| --- | --- |
| Map Workspace Contract | Provides `table_rows`, `map_pins`, `selected_record`, `result_counts`, and `available_filters` for a synchronized map/table workspace. Supports property type, record type, status, verification status, stale flag, city, and state filters. |
| Assignment Profile | Provides metadata-only assignment context, file-group counts, completeness, and routing hints for future review. Useful for empty-state explanation, assignment context, and metadata-only provenance labels. |
| Firm Intelligence Card | Provides a concise summary surface with order summary, match groups, top match cards, confidence/provenance summary, warnings, and recommended actions. Useful for workspace summary and cross-entry from Falcon Core surfaces. |
| Passport Model | Provides fact identity, display value, verification/review fields, confidence dimensions, evidence links, audit event IDs, and searchable status. Supports the Passport drawer. |
| Evidence Link Model | Provides metadata-only evidence rows with access level, source document type, display label, status, and future anchors that remain placeholders. Supports Evidence drawer row rendering and disabled states. |
| Evidence Open Contract | Validates that an evidence ID belongs to a passport and returns a metadata-only evidence summary plus suggested audit payload. Supports Evidence drawer ready/unavailable/permission states without source preview. |
| Audit Event Model | Provides stable synthetic audit event envelopes for card viewed, passport detail opened, evidence opened, and historical comparable justification. Supports audit handoff and initial audit drawer summaries. |
| Permission Policy | Provides stable role codes, permission action codes, decision objects, reason codes, and reason labels. Supports workspace, passport, evidence, audit, disabled, and hidden states. |
| Manifest Search | Provides metadata-only search over saved manifests, including file names, extensions, relative paths, modified timestamps, summary counts, and report-candidate hints. Supports future metadata context and no-source-content guardrails. |
| Metadata Scanner | Provides metadata-only file records and supported-future-indexing flags. Supports future local scan context and safe explanations of why content is not searchable yet. |
| Falcon API Contracts | Provides local Falcon-style card, passport detail, and evidence-open response envelopes, including permission-denied shapes and suggested audit payload placement. Supports frontend API boundary simulation. |
| Schema Registry | Provides current schema names, versions, intended consumers, fixture paths, and breaking-change rules. Supports version checks and snapshot-aware UI development. |
| Snapshot Suite | Provides stable JSON fixtures for card, passport drawer, map workspace response, Falcon API envelopes, and audit event envelopes. Supports first React development without production services. |

## UI Readiness Matrix

Status definitions:

- READY: can be implemented directly from existing contracts.
- DERIVED: requires UI composition only. No schema changes.
- DEFERRED: intentionally future roadmap work.

| Feature | Existing Contract | Status | Notes |
| --- | --- | --- | --- |
| Falcon shell integration | `docs/intelligence-workspace-falcon-shell-integration.md` | DERIVED | Shell, sidebar, top nav, labels, and hierarchy are documented. React can compose these from Falcon shell primitives rather than Intelligence schemas. |
| Workspace header | Map Workspace Contract; Falcon shell integration doc | DERIVED | Header can derive title, result counts, selected scope, and status labels from `result_counts`, selected record, and shell context. |
| Filter rail | Map Workspace Contract | READY | `available_filters` and supported filter keys are present. UI can render the first rail directly from v1. |
| Map canvas | Map Workspace Contract | READY | `map_pins` includes IDs, coordinates, labels, types, statuses, verification state, and selection state. First implementation can use synthetic coordinates and a non-production map renderer. |
| Map markers | Map Workspace Contract | READY | Marker identity and visual states can be rendered from `map_pins`, `verification_status`, `record_type`, `stale_flag` via matching table rows, and `is_selected`. |
| Marker clustering | Map Workspace Contract | DERIVED | Cluster groups can be computed client-side from visible pins. No schema change is required for a first preview. Production clustering rules can be deferred. |
| Bottom synchronized table | Map Workspace Contract | READY | `table_rows` provides row payloads and selected state. Existing fields cover the first table columns. |
| Marker/table synchronization | Map Workspace Contract | READY | Shared row/pin IDs and `is_selected` support click synchronization. UI can maintain selected ID state and request/recompute the response. |
| Passport drawer | Passport Model; Passport Detail Drawer snapshot; Falcon Passport Detail API envelope | READY | Existing drawer contract supports fact summary, verification/review summary, confidence dimensions, evidence summaries, audit IDs, searchable status, and warnings. |
| Evidence drawer | Evidence Link Model; Evidence Open Contract | READY | Evidence rows and metadata-only evidence-open responses support drawer rendering, disabled states, permission denied, and audit handoff. |
| Audit drawer | Audit Event Model; Data Passport audit IDs; Audit snapshots | DERIVED | Full durable timeline is not present, but first drawer can render available audit IDs, snapshot-backed event summaries, unavailable states, and synthetic limitation messaging. No schema change required. |
| Permission states | Permission Policy; Falcon API Contracts | READY | Stable decisions, reason codes, reason labels, and `permission_denied` envelope shape support UI access states. |
| Loading states | Workspace State Model; Falcon API Contracts | DERIVED | Loading is UI lifecycle state and should not be added to data schemas. |
| Empty states | Workspace State Model; Map Workspace Contract; Manifest/Assignment docs | DERIVED | True empty can be derived from no source records or zero total count. Copy and behavior are documented. |
| No-results states | Map Workspace Contract; Workspace State Model | READY | `result_counts.total_records` and `result_counts.filtered_records` distinguish no-results from empty. |
| Context Bar | Shell Integration doc; Map Workspace Contract; Passport Model | DERIVED | Context sentence can be composed from `result_counts`, selected record, passport fact summary, verification/review fields, and evidence/audit selection. No new schema is required. |
| Layer panel | Shell Integration doc; Map Workspace Contract | DERIVED | Initial layers can be UI toggles over existing `record_type`, `verification_status`, and stale fields. Advanced GIS layers are deferred. |
| Workspace summary | Map Workspace Contract; Firm Intelligence Card | READY | `result_counts` and card summary data support a compact workspace summary. |
| Workspace badges | Map Workspace Contract; Permission Policy; Passport Model | DERIVED | Badges can be derived from verification status, stale flag, permission decisions, searchable status, and evidence availability. |
| Verification indicators | Map Workspace Contract; Passport Model; Firm Intelligence Card | READY | `verification_status`, passport verification/review summaries, and card provenance fields support verified/reviewer/pending indicators. |
| AI suggestion pending | Workspace State Model; Passport/Data Model docs | DEFERRED | Future-facing state. It can be represented visually later, but real suggestion generation is blocked. |
| Reviewer approval pending | Workspace State Model; Passport Model | DERIVED | Current passport review fields can support pending copy when data exists. Formal production review workflow remains future. |
| Production data replacement | Schema Registry; Falcon API Contracts; Snapshot Suite | DEFERRED | React can target current envelope shapes now; production data can later replace synthetic sources behind the same or versioned contracts. |

## Potential Gaps

No required schema changes were identified for the first React workspace preview.

Potential gaps should be handled as follows:

| Potential gap | Assessment | Recommendation |
| --- | --- | --- |
| Full audit timeline | Existing contracts provide audit event IDs, suggested audit payloads, and snapshot-backed event shapes, not durable timeline retrieval. | Derive a first audit drawer from available audit IDs, event snapshots, and "timeline unavailable in synthetic workspace" states. Do not add schema until production audit persistence is approved. |
| Advanced marker clustering metadata | The map contract does not include cluster IDs or precomputed cluster summaries. | Compute clusters client-side from visible pins for the preview. Defer provider-grade clustering until production map strategy is approved. |
| Layer-specific counts beyond current filters | The map response includes counts by record type and stale count, but not every future layer count. | Derive initial layer states from `record_type`, `verification_status`, and stale fields. Defer advanced layer analytics. |
| Context Bar exact sentence payload | No dedicated context-bar schema exists. | Compose the sentence from selected record, result counts, passport summary, evidence summary, and audit focus. A dedicated schema is not needed for the first preview. |
| Workspace loading/error states | Loading and error are not data contract fields. | Keep them as React lifecycle and boundary states. Do not add backend fields. |
| Real map provider behavior | No production map provider contract exists. | Use synthetic coordinates in a local/static renderer for preview. Production provider integration remains deferred. |

The preferred outcome remains: no required schema changes.

## React Build Order

Recommended implementation sequence:

1. Falcon shell integration.
2. Workspace layout.
3. Synthetic map rendering.
4. Bottom synchronized table.
5. Marker/table synchronization.
6. Passport drawer.
7. Evidence drawer.
8. Audit drawer.
9. Workspace state handling.
10. Context Bar.
11. Layer panel.
12. Interaction polish.
13. Accessibility pass.
14. Performance optimization.
15. Production data replacement, future only.

Build notes:

- Start from committed snapshots rather than production services.
- Keep selected record ID as UI state.
- Derive marker, table, drawer, and Context Bar state from existing payloads.
- Treat unavailable audit/source preview paths as documented states, not blockers.
- Preserve schema version checks and snapshot compatibility.

## Architecture Assessment

Is the backend architecture ahead of the UI?

Yes. The repository already has synthetic/local contracts, schema registry entries, snapshot fixtures, permission scaffolding, audit event envelopes, map workspace serialization, passport/evidence contracts, and smoke tests before any React workspace exists.

Does the current synthetic contract model appear sufficient?

Yes. The current model is sufficient for a first internal React preview of the Intelligence Map workspace, including filter rail, map pins, bottom table, synchronized selection, passport drawer, evidence drawer, permission states, workspace states, and derived context summary.

Can React begin without additional backend work?

Yes. React can begin against static snapshots and local synthetic contract helpers. No additional backend architecture is required for the first preview.

Can production data later replace synthetic snapshots without redesigning the UI?

Yes, if production data conforms to the same schema versions or intentionally versioned successors. The UI should target the registered contract shapes and treat production replacement as a data-source swap behind stable envelopes, not a redesign.

## Recommendations

- Begin React implementation against existing v1 synthetic contracts.
- Reuse existing contracts before proposing schema changes.
- Derive UI state for loading, empty, no-results, stale, permission, context bar, badges, layers, and clustering.
- Delay schema expansion until a concrete UI behavior cannot be derived from current payloads.
- Preserve snapshot compatibility and review JSON diffs deliberately.
- Keep source preview, production map provider, production auth, production database, extraction, OCR, embeddings, and OneDrive out of the first React preview.
- Treat audit timeline limitations as an explicit UI state rather than a blocker.
- Keep the first React slice internal-only, synthetic-only, and Falcon-shell-aligned.

## V2D Conclusion

Falcon Intelligence can begin the first React workspace implementation using the existing v1 synthetic contracts. No required schema changes were identified.

The contract model is ready for UI composition. The next slice should implement a minimal internal React preview against snapshots, while preserving the roadmap philosophy of trust first, implementation second.

