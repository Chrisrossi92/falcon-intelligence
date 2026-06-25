# Intelligence Workspace State Model

This document defines canonical UI states for the Falcon Intelligence Map workspace. It is documentation-only. It does not authorize React UI, backend architecture, new schemas, real data access, OneDrive access, extraction, OCR, embeddings, source-document preview, production database/auth, or production map provider integration.

The Map workspace must feel trustworthy when data is missing, stale, blocked, unavailable, or still awaiting verification. Trust is the product. Bad states should be explicit, calm, and actionable without implying that Falcon Intelligence has reached a valuation conclusion.

## State Principles

Workspace states should follow the Falcon shell direction:

- Calm, operational, professional, and restrained.
- Minimal scrolling and no wall-of-cards fallback pages.
- Clear labels, direct language, and progressive disclosure.
- Drawers for detail, not full-page detours.
- No gimmicky AI visuals, glowing gradients, or "black box" language.
- No fake confidence, fake counts, or synthetic optimism while data is resolving.
- No restricted facts, counts, evidence IDs, source metadata, or audit details shown to users who lack access.

Every state should help the user understand one of four things:

| Question | State responsibility |
| --- | --- |
| Where is it? | Map/table context, filter scope, and location availability. |
| What do we know? | Whether verified intelligence exists and whether it is searchable. |
| Why do we believe it? | Evidence availability, evidence limitation, and provenance fallback. |
| Who verified it? | Audit availability, permission state, and reviewer accountability. |

## State Priority Order

When multiple states could apply, use this priority order:

1. Permission denied.
2. Error.
3. Loading.
4. Empty.
5. Stale.
6. No results.
7. Content available.

Nested drawers should apply the same logic within their own scope. For example, a workspace can be content available while the evidence drawer is permission denied, or the map can be stale while the audit drawer is unavailable.

## Empty State

Use the empty state when no synthetic assignments or verified intelligence are available to the workspace at all. This is different from filters returning no rows.

Message:

- Primary: "No verified intelligence is available yet."
- Secondary: "Falcon Intelligence only shows records after eligible synthetic assignments or verified facts are available to this workspace."

Visual treatment:

- Keep the full workspace frame visible: filter rail, empty map area, and empty table area.
- Use one compact, centered workspace message inside the map/table area.
- Do not replace the workspace with a marketing page.
- Do not show decorative illustrations or AI-themed empty art.
- Use restrained neutral styling consistent with the Falcon shell.

Allowed actions:

- View disabled filter controls if available filter values are empty.
- Open module-level help or a future "how intelligence becomes searchable" note.
- Return to Falcon Core order or assignment context when entered from Core.

Disabled actions:

- Opening a passport.
- Opening evidence.
- Opening audit history for a record.
- Selecting a marker or table row.
- Using map layers that require records.

User reassurance:

- Explain that the state is not a valuation or market conclusion.
- Explain that the absence of surfaced intelligence does not prove the firm has no historical knowledge.
- Explain that searchability requires eligible records, verification, permissions, and tenant policy.

Searchability language:

- "This workspace does not have verified searchable intelligence yet."
- "Facts become searchable only after verification and permission checks."

## Loading State

Use loading when synthetic workspace data, filters, or drawer detail is resolving.

Message:

- Primary: "Loading workspace intelligence."
- Secondary: "Verified records, filters, and map locations are being prepared."

Map skeleton behavior:

- Show a quiet map skeleton or neutral map placeholder.
- Do not show sample markers.
- Do not show implied clusters.
- Do not animate confidence states.

Table skeleton behavior:

- Show stable placeholder rows only when the table structure is known.
- Avoid placeholder text that looks like real property data.
- Do not show counts until the contract response is available.

Drawer behavior:

- If a passport, evidence, or audit drawer is opened from an existing selected record, keep the drawer shell and show a compact loading state.
- Do not clear map/table context while drawer detail is loading.
- If workspace-level loading begins after a filter change, preserve prior context only when it is visibly marked as updating.

Filter rail behavior:

- Keep filters visible.
- Disable filter changes while the new result set is resolving if concurrent updates would create ambiguous state.
- Do not show unavailable filter values as if they are confirmed.

No fake confidence:

- Loading states must not show confidence values, verification badges, result totals, or stale warnings until those values come from the current synthetic contract response.

## Permission Denied State

Use permission denied when the current actor lacks access under the local Permission Policy or future Falcon production auth. Permission denial is highest priority because hidden intelligence must remain hidden even when other states also apply.

Workspace-level denial:

- Client users should not see Intelligence surfaces.
- Internal denied users may see a minimal unavailable workspace shell only when useful for support.
- Do not reveal record counts, property labels, passport IDs, evidence IDs, source labels, audit IDs, or denied record types.

Suggested message:

- Primary: "Falcon Intelligence is not available for your role."
- Secondary: "Access to internal intelligence is controlled by firm policy."

Property-level denial:

- The map/table may show only records the actor is permitted to know exist.
- Restricted records should not appear as blurred markers if their existence is sensitive.
- If a visible row has a disabled passport action, the reason should be generic: "Passport access is restricted."

Evidence-level denial:

- Evidence rows may appear only when the actor is allowed to see their metadata.
- The open action should be disabled with restrained text: "Evidence access is restricted."
- Do not expose future page anchors, source document IDs, path-like labels, or source metadata to denied users.

Audit-level denial:

- Audit affordances should be hidden or disabled depending on policy.
- Use generic language: "Audit history is restricted for your role."
- Do not reveal whether a sensitive audit event exists.

Disabled UI treatment:

- Use standard disabled controls, neutral text, and concise tooltips or inline reasons.
- Avoid red error styling unless a user action has failed.
- Keep disabled actions visible only when their existence does not leak restricted facts.

Explainable without leakage:

- It is acceptable to show stable reason labels from the Permission Policy when they do not disclose sensitive facts, such as client-role denial.
- It is not acceptable to show restricted match counts, evidence identities, source labels, or hidden property summaries.

## Stale Data State

Use stale data state when synthetic manifest, scan metadata, map record `stale_flag`, or confidence/provenance fields indicate records may be out of date.

Banner behavior:

- Show a compact workspace banner when stale data affects the current result set.
- Keep it below the workspace header and above the map/table area.
- Do not block the workspace unless policy requires justification before use.

Suggested message:

- Primary: "Some intelligence may be stale."
- Secondary: "Review verification dates, stale warnings, and supporting evidence before relying on these records."

What remains usable:

- Map orientation remains usable.
- Table scanning remains usable.
- Passport drawer remains usable if permitted.
- Evidence and audit remain usable if permitted.
- Filtering by stale status should remain available when supported by the map workspace contract.

What should be visually cautioned:

- Stale map markers.
- Stale table rows.
- Passport freshness fields.
- Evidence summaries tied to old verification or source dates.
- Historical comparable actions that may require justification.

Provenance/audit language:

- Use "verified on", "reviewed on", "stale after", and "last scan metadata" language where available.
- Avoid implying stale records are wrong.
- Avoid implying stale records are safe to reuse without review.
- When reuse is possible, show that appraiser justification or reviewer approval may be required by policy.

## No-Results State

Use no-results when the workspace has available records, but the current filters or search return no matching map/table rows.

Message:

- Primary: "No records match the current filters."
- Secondary: "Adjust filters to expand the workspace result set."

Table state:

- Keep table headers visible.
- Show one compact empty row or table body message.
- Do not show a true-empty onboarding message.

Map state:

- Keep the map canvas visible.
- Show no markers for the filtered result set.
- If map bounds are retained, make clear that markers are hidden by filters, not missing from the system.

Filter reset behavior:

- Offer a clear "Reset filters" action.
- Preserve the user's last selected filters until they reset or edit them.
- If a selected record is filtered out, clear the selection and close or mark drawers as out of scope.

Difference from true empty state:

- No-results means the workspace has records outside the current filter/search scope.
- Empty means the workspace has no eligible synthetic assignments or verified intelligence to show.

## Evidence Unavailable State

Use evidence unavailable when a fact exists but the evidence link cannot be opened from the current workspace. Evidence unavailable is not the same as no evidence exists.

Evidence contract behavior:

- Use the evidence link model and evidence-open response status to decide whether evidence is available, disabled, not found, permission denied, or preview blocked.
- A successful evidence-open response is still metadata-only in the current repository.
- Do not open files, render source documents, read report contents, or show source text.

Suggested messages:

- Disabled: "This evidence cannot be opened from the current workspace."
- Preview blocked: "Source preview is not enabled for this workspace."
- Not found: "This evidence link is no longer available."
- Permission denied: "Evidence access is restricted for your role."

Provenance fallback:

- Keep the passport visible if permitted.
- Show safe provenance fields already present on the passport: verification status, confidence dimensions, source type labels, evidence count, and audit event IDs.
- Do not substitute raw source text or guessed summaries.

Open action disabled reason:

- Disable "open evidence" actions with a concise reason.
- Prefer specific but safe reasons, such as "preview blocked" or "restricted", when they do not leak source details.

Audit still available:

- Audit history may remain available if permitted.
- Opening evidence should not be logged as successful when evidence did not open.
- If production audit later records denied or failed attempts, Falcon Core must persist those events through its durable audit service.

## Audit Unavailable State

Use audit unavailable when audit history cannot be viewed for a selected record, evidence item, or passport.

Distinguish the reason:

- Permission: the actor is not allowed to view audit history.
- Missing history: the record has no associated audit events in the current synthetic fixture.
- Synthetic limitation: the current local contract provides suggested audit payloads or event IDs but not a full durable audit timeline.

Suggested messages:

- Permission: "Audit history is restricted for your role."
- Missing history: "No audit history is available for this record."
- Synthetic limitation: "Audit timeline is not available in the current synthetic workspace."

What should not be implied:

- Do not imply the fact is unverified merely because the audit drawer is unavailable.
- Do not imply audit events were deleted.
- Do not imply production persistence exists in the current local prototype.
- Do not show stack traces, raw event payloads, or internal identifiers as the primary user message.

Fallback behavior:

- Keep passport verification/review summaries visible when permitted.
- Keep evidence metadata visible when permitted.
- Keep the drawer context stable so the user can close audit and return to the passport.

## AI Suggestion Pending State

This state is future-facing only. It must not be implemented as real extraction, OCR, embeddings, or model-assisted content review in the current milestone.

Meaning:

- A future system or workflow has suggested a fact, comp, market indicator, reviewer note, or relationship.
- The suggestion is not verified firm knowledge.
- The suggestion is not searchable knowledge by default.
- Human verification is required before it becomes reusable intelligence.

Visual treatment:

- AI-suggested facts must be visually distinct from verified knowledge.
- Use subdued pending styling, not bright confidence badges.
- Do not place AI suggestions in the same visual hierarchy as verified records.

Suggested copy:

- "This fact is not searchable until verification is complete."
- "Suggested intelligence requires appraiser or reviewer verification."

Disabled actions:

- Firm-search reuse.
- Comparable selection as verified knowledge.
- Report language generation.
- Any action that implies professional conclusion.

## Reviewer Approval Pending State

This state is future-facing only and depends on firm policy.

Meaning:

- An appraiser may have verified a fact, but reviewer approval is still pending for searchability, reuse, QA sensitivity, stale override, or comparable use.
- Reviewer approval is separate from appraiser verification when policy requires both.

What can appear:

- The fact may appear in a passport as appraiser-verified but reviewer-pending.
- It may appear in review queues or restricted internal views.
- It may appear with disabled reuse/search actions if policy blocks use until reviewer approval.

What cannot appear:

- It should not appear as ordinary firm-searchable verified knowledge when reviewer approval is required and incomplete.
- It should not appear as a fully approved comparable, market indicator, or reusable report support fact.

Traceability requirements:

- Show who verified the fact and when, if permitted.
- Show reviewer status separately.
- Preserve audit event references or future audit timeline links.
- Avoid combining appraiser verification and reviewer approval into one ambiguous "approved" badge.

Suggested copy:

- "Verified by appraiser; reviewer approval pending."
- "This fact is not searchable until required review is complete."

## Error State

Use error when synthetic contract loading fails, a contract response is malformed, or the workspace cannot safely render the response.

Message:

- Primary: "Falcon Intelligence is temporarily unavailable."
- Secondary: "The workspace could not load the current synthetic contract data."

Visual treatment:

- Keep the workspace frame visible when possible.
- Use a compact platform-aligned error message.
- Do not show stack traces, raw JSON, Python exceptions, request payloads, or internal paths in the UI.
- Do not expose partial sensitive data from a failed response.

Allowed actions:

- Retry.
- Reset filters if filter state may be involved.
- Return to Falcon Core context.
- Copy or reference a safe diagnostics ID if available.

Diagnostics/audit reference:

- If a safe request ID, diagnostics ID, or future audit reference exists, show it in small secondary text.
- Do not imply durable production audit persistence exists in the current local prototype.

## Contract Mapping

The V2B state model uses existing contracts. It does not add a new schema.

| State input | Existing source | Informs |
| --- | --- | --- |
| Permission Policy | `src/falcon_intel/permission_policy.py`; `docs/data-confidence-provenance-model.md`; `docs/falcon-ui-integration-notes.md` | Workspace, property, passport, evidence, audit, and disabled access states. |
| Map Workspace Contract | `docs/intelligence-map-workspace-contract.md`; `tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json` | Content available, no-results, selected record, result counts, stale counts, filter availability, map/table sync. |
| Evidence Open Contract | `src/falcon_intel/falcon_evidence_contract.py`; `tests/fixtures/synthetic_api_envelopes/falcon-evidence-open-api-response-v1.json` | Evidence ready, unavailable, not found, permission denied, preview blocked, and suggested audit handoff. |
| Evidence Link Model | `src/falcon_intel/evidence_link.py`; `docs/data-confidence-provenance-model.md` | Evidence metadata, access level, disabled status, source type label, future anchors that remain non-content placeholders. |
| Audit Event Model | `src/falcon_intel/audit.py`; `tests/fixtures/synthetic_audit_events/`; `docs/intelligence-match-policy.md` | Audit available, audit unavailable, suggested audit event handoff, historical comp justification traceability. |
| Assignment Profiles | `docs/assignment-profiles.md`; `tests/fixtures/synthetic_profiles/` | Empty state explanation, assignment context, metadata-only provenance, stale scan context. |
| Manifest Search | `docs/manifest-search.md`; `docs/metadata-scanning.md` | Metadata availability, no searchable metadata, scan-derived context, stale or missing manifest explanations. |
| Schema Registry / Changelog | `docs/schema-version-registry.md`; `docs/schema-changelog.md` | Contract version awareness, unsupported schema error handling, deliberate snapshot review before schema changes. |

## Copy Guidelines

Prefer plain, defensible language:

- "No verified intelligence is available yet."
- "No records match the current filters."
- "This evidence cannot be opened from the current workspace."
- "This fact is not searchable until verification is complete."
- "Audit history is restricted for your role."
- "Some intelligence may be stale."

Avoid magical or conclusive language:

- Do not say "AI found the answer."
- Do not say "best comp" unless an appraiser has made that selection in an approved workflow.
- Do not say "verified by AI."
- Do not say "no firm knowledge exists" when only current eligible results are empty.
- Do not say "safe to rely on" for stale or evidence-unavailable records.
- Do not describe suggested facts as searchable intelligence.

Status labels should be short, professional, and tied to action:

- Verified.
- Suggested.
- Reviewer pending.
- Stale.
- Evidence unavailable.
- Access restricted.
- Preview blocked.
- No matching records.

## V2B Completion Criteria

V2B is complete when:

- The canonical workspace state model is documented.
- Empty, loading, permission denied, stale, no-results, evidence unavailable, audit unavailable, AI suggestion pending, reviewer approval pending, and error states are defined.
- State priority order is explicit.
- Existing synthetic contracts are mapped to state inputs.
- Falcon shell and copy guidance are documented.
- No React UI, backend architecture, schema changes, real extraction, OCR, embeddings, source preview, OneDrive access, production auth, production database, or production map provider work is added.

