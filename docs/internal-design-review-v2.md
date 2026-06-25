# Falcon Intelligence Internal Design Review V2

This document reviews the internal React preview after V2M. It is documentation-only and does not authorize UI implementation, feature expansion, schema changes, backend architecture, production map provider integration, real data access, source preview, extraction, OCR, embeddings, OneDrive access, production authentication, or production database work.

The review evaluates the preview as if an experienced commercial appraiser were seeing Falcon Intelligence for the first time.

## Summary

The current preview successfully establishes Falcon Intelligence as a calm, professional, trust-oriented workspace rather than a generic AI dashboard. The strongest product idea is clear: the user starts with spatial orientation, selects a property, opens a Passport, reviews Evidence, and can inspect Audit context while preserving map and table context.

The experience is credible enough to serve as the first UX blueprint for Falcon Intelligence, but it is not yet production-ready as a complete user experience. The main gaps are not technical capability; they are product clarity, workflow guidance, and information hierarchy. A new appraiser can infer the workflow, but the preview still asks the user to discover too much through interaction. The trust model is present, but verification, evidence, and audit status could be more intentionally staged across the map, table, summary, and drawers.

Overall, the direction is right. The next phase should preserve the current structure and improve explanation, state clarity, and review ergonomics rather than expanding features.

## Overall Score

Internal-only score: 7.4 / 10.

Rationale:

- Strong foundation: Falcon-like shell, restrained visual system, preserved context, and clear provenance surfaces.
- Main weakness: the experience explains itself better after interaction than at first glance.
- Production UX readiness: good blueprint, not yet a finished production interaction model.

## 1. Overall First Impression

The preview immediately communicates that this is an internal workspace for verified property intelligence. The map, table, selected summary, and drawers form a coherent appraisal-review environment. It feels closer to an appraisal operations platform than to an AI product, which is correct for Falcon Intelligence.

The shell feels Falcon-like enough for an internal preview. The dark sidebar, restrained workspace header, compact Context Bar, and dense lower table all support a professional platform feel. The visual system is premium in the sense of being controlled and sober, not flashy.

Trust is visible through the labels "Verified knowledge," "Evidence available," "Audit activity," Passport/Evidence/Audit drawer progression, and the repeated synthetic-only and appraiser-judgment copy. Nothing suggests automatic valuation conclusions.

Immediate distractions:

- The preview-only state simulator is correctly separated, but its presence in the header still competes with the workspace summary. That is acceptable for internal review but should not influence the production header model.
- The Layer Panel overlays the map and can visually compete with the selected marker area. It is useful but makes the map feel partly controlled by an inspector panel rather than fully spatial.
- The table and selected summary are strong, but at first glance they may pull attention away from the map because they contain more readable text than the map canvas.

## 2. Visual Hierarchy

Shell:

The shell is calm and credible. Intelligence is clearly selected and does not feel like a separate brand. The sidebar gives platform context without trying to explain the Intelligence module.

Header:

The header labels the workspace clearly. "Synthetic internal preview using v1 contracts. Appraiser judgment remains final." is strong for internal safety, but it reads as implementation context rather than product context. Production UX should keep the human-responsibility concept but avoid contract language in the primary header.

Context Bar:

The Context Bar is useful and placed correctly. It explains current knowledge context without becoming breadcrumbs. It is visually quiet enough to fit Falcon, but possibly too quiet for a first-time user to understand that it is the workspace's live explanation layer.

Filter rail:

The filter rail feels operational and appropriate. It does not dominate the workspace. It currently reads as a static scope summary more than a powerful filtering surface, which is acceptable for the preview.

Map:

The map is visually primary by size and placement. The coordinate-plane styling is clearly a placeholder but not gimmicky. The map is calm and avoids fake GIS precision.

Layer panel:

The Layer Panel is readable and useful, but it floats over the primary workspace. It can visually suggest that layers are more important than selection. It should eventually feel like a map tool attached to the map, not a separate inspector.

Table:

The table is the most information-dense surface and explains the map well. Row selection is visible. The density is professional, but the table can dominate the user's understanding because it contains the clearest property labels.

Selected summary:

The summary panel is helpful and correctly compact. It bridges the map/table selection to Passport. It could do more to reinforce "what do we know now?" before the drawer opens.

Passport:

The Passport drawer is clear and appropriately structured. It is the best expression of the product's trust model, but some sections feel equally weighted even though identity, verified fact, evidence, and review should not all have the same priority.

Evidence:

The Evidence drawer makes metadata-only limitations explicit. It preserves trust by not pretending to show source documents. The audit handoff is clear.

Audit:

The Audit drawer is understandable and preserves context. The timeline is credible as a preview, but it still feels more like a system event list than a reviewer accountability surface.

Overall hierarchy:

The eye is guided reasonably well through shell -> header -> map -> table/summary -> drawers. The weakest hierarchy transition is from selected property summary to Passport; the "Open passport" action is clear, but the summary could better preview why the Passport matters.

## 3. Workflow

The intended flow is:

```text
Map
-> Property
-> Passport
-> Evidence
-> Audit
```

This flow is understandable after a user clicks a marker or row. It is not fully self-evident before interaction. An appraiser will likely understand map/table selection quickly, but Passport, Evidence, and Audit are specialized terms that need context.

What works:

- Marker and row selection synchronize.
- The selected summary provides a natural next step.
- Passport opens without losing map/table context.
- Evidence opens from Passport.
- Audit opens from Evidence.
- Closing nested drawers preserves the parent context.

What is less obvious:

- Why a user should open a Passport instead of relying on the table row.
- Whether Evidence is always metadata-only or only unavailable in the preview.
- Whether Audit means user activity, verification history, reviewer approval, or all of those.
- Whether layer toggles are filtering data, changing badges, or both.

Workflow clarity is good for an internal milestone and not yet ready for unsupervised production onboarding.

## 4. Information Density

The information density is appropriate for an appraiser-facing professional tool. It is denser than a consumer dashboard and lighter than a full appraisal workfile. That is the right balance.

Too much information:

- The Passport drawer repeats identity, context, evidence, review, and warnings at similar visual weight. This may slow scanning.
- Evidence includes several metadata rows that are useful but could become repetitive across records.
- The state simulator adds internal implementation noise to the header.

Too little information:

- The map markers do not communicate enough at rest. The selected marker is visible, but non-selected marker meaning is mostly hidden until hover/focus.
- The selected property summary could surface stronger trust cues before opening Passport: verified fact count, evidence availability, and audit status.
- The Context Bar could be more discoverable as the live explanation of current context.

Information to hide later:

- Synthetic-only implementation language.
- Detailed metadata rows in Evidence when they are not decision-critical.
- Repeated identity fields across Passport, Evidence, and Audit once the hierarchy is stable.

Information to surface earlier:

- Why the selected property matters.
- Whether the selected item has Passport/Evidence/Audit coverage.
- Whether the visible result set is fully verified, partially verified, stale, or permission-limited.

## 5. Map Emphasis

The map feels primary by layout area. It is the largest canvas and anchors the workspace. However, the table currently carries more semantic meaning because text labels, statuses, and badges are more readable there.

The map does not yet fully answer "Where is it?" beyond plotting synthetic points. That is acceptable for a no-provider preview, but the product goal will eventually require richer spatial context.

Recommended UX improvements:

- Make selected marker context more informative without overwhelming the map.
- Keep the table visually subordinate to the map, but let it remain the structured explanation surface.
- Consider moving or compressing the Layer Panel if it obscures too much map space.
- Give the map a clearer selected-location label that explains the chosen property, not just the marker name.

The map is primary structurally, but the table is primary informationally. Future polish should bring those into better balance.

## 6. Drawer Experience

Passport:

The Passport drawer preserves context and clearly answers "What do we know?" It has the right sections: identity, verified fact, confidence/provenance, related context, evidence metadata, verification review, warnings.

Concerns:

- Several sections are equally weighted, so the user must decide what matters.
- Identity fields may be too prominent for appraisers compared with fact, evidence, and review status.
- The drawer could benefit from progressive disclosure or collapsed advanced metadata after the top trust summary is established.

Evidence:

The Evidence drawer answers "Why do we believe it?" in a safe metadata-only way. It is clear that source preview is not available. This is a strong trust-preserving choice.

Concerns:

- Evidence identity and provenance can feel repetitive.
- "Open status" and "metadata-only" concepts are useful internally but may need more user-facing language later.
- The audit handoff is clear, but it may be visually too similar to other drawer sections.

Audit:

The Audit drawer answers "Who verified it?" and "what happened?" but not always with the appraiser/reviewer emphasis a commercial appraisal team may expect. Timeline rows are useful, yet they read like system logs more than review accountability.

Concerns:

- Audit event names need to be translated into plain reviewer/accountability language.
- Actor, timestamp, and status should become more scannable.
- The distinction between "synthetic preview event" and production audit history must remain explicit.

Depth:

Three nested drawers is acceptable for this product because the hierarchy is trust-driven and context-preserving. It does not feel too deep in the preview, but production will need careful focus, width, and escape/close behavior across smaller screens.

## 7. Context Bar

The Context Bar is genuinely helpful. It does not behave like breadcrumbs; it explains the current knowledge context. This matches the V2C concept well.

Strengths:

- It updates across workspace, selected property, Passport, Evidence, Audit, and bad states.
- It uses plain language.
- It remains calm and compact.

Concerns:

- It may be too subtle for new users to notice.
- Some sentences are long enough to truncate before the most useful detail appears.
- It sometimes sounds like status telemetry rather than product guidance.

Recommended direction:

- Keep it compact.
- Put the most important object first.
- Keep counts and status second.
- Avoid implementation phrases.
- Consider making it visually stronger only when selection depth changes.

Current verdict: keep it. It is a differentiating Falcon Intelligence pattern.

## 8. Layer Panel

The Layer Panel is useful because it introduces the idea that the map can represent different intelligence layers without adding production GIS complexity.

Strengths:

- Labels are understandable.
- Future/deferred layers are clearly disabled.
- It distinguishes verified knowledge, reports, evidence, and audit activity.
- It avoids AI-first visual language.

Concerns:

- "Subjects" currently controls base visibility, while other layers mostly control details or badges. This mixed behavior could confuse users.
- "Reports" may be interpreted as source-document access, which is not available.
- "Reviewer/Audit Activity" is long and may become awkward as layers scale.
- The overlay placement may compete with map selection.

Future scalability:

The panel can scale conceptually, but it will need grouping before adding Sales, Leases, Market Areas, Comparable Clusters, AI Suggestions, and Reviewer Flags. Without grouping, it will become a long control list.

## 9. Trust Model

The trust model is the preview's strongest product advantage. Verification, evidence, audit, and appraiser responsibility are visible throughout the experience.

What works:

- "Appraiser judgment remains final" appears early.
- Verified knowledge badges reinforce the status model.
- Evidence and Audit are treated as first-class drawers, not hidden metadata.
- Source preview is explicitly not shown.
- Unavailable states are calm and honest.
- Closing drawers preserves context.

What could improve:

- The trust model is present but distributed. A first-time user may need to open multiple surfaces before understanding the full chain.
- Verification, evidence, and audit could be summarized more clearly at the selected property level.
- Audit should feel more like reviewer accountability, less like event telemetry.

The UI reinforces trust without becoming noisy, but it needs a clearer top-level "why trust this selected item?" summary.

## 10. Accessibility UX

At a UX level, keyboard navigation is in a good internal-preview state. Markers, table rows, layer toggles, selected summary actions, and drawer controls are reachable and usable. Escape behavior for nested drawers is intuitive.

Strengths:

- Keyboard users can select markers and rows.
- Escape closes deepest drawer first.
- Focus moves into drawers after opening.
- Disabled Passport actions are not activatable.
- Layer controls are standard inputs.

Potential UX issues:

- Power users may need faster row-to-drawer workflows.
- Table row focus and nested button focus may feel redundant.
- No explicit keyboard affordance is visible to users.
- Deep drawer stacks may become hard to manage on smaller screens even if keyboard behavior is correct.

This is not a production accessibility audit, but the interaction model is directionally sound.

## 11. Consistency

Interactions are mostly consistent:

- Marker and table row selection synchronize.
- Drawers open from the previous trust surface.
- Closing nested drawers returns to parent context.
- Escape closes in the expected order.
- Disabled states avoid fake action.

Terminology is mostly consistent:

- Passport, Evidence, Audit, Verified, Metadata-only, Synthetic, and Preview all appear repeatedly.
- Some implementation terms remain visible, including "v1 contracts," "synthetic workspace," and "preview-only state simulator." These are appropriate for internal review, but not for production UX.

Inconsistencies to address later:

- Layer toggles mix filtering and badge visibility.
- Audit terminology mixes event codes and user-facing review concepts.
- Evidence availability sometimes reads as a product limitation and sometimes as a permission/open status.
- "Report metadata" could imply report access.

## 12. What Feels Unfinished

Prototype feel:

- Synthetic coordinate-plane map.
- Preview-only state simulator in the header.
- Synthetic/internal copy in primary surfaces.
- Some marker labels appear only on hover/focus.
- Layer Panel overlay feels like a prototype inspector.

Placeholder feel:

- Future disabled layers.
- Metadata-only evidence without richer provenance summary.
- Audit timeline events with synthetic timestamps and system-like phrasing.
- No real map provider or spatial context, intentionally deferred.

Rough or inconsistent:

- Drawer sections have equal weight and could be more scan-optimized.
- Context Bar is helpful but under-emphasized.
- The selected property summary is useful but not yet a strong trust summary.
- Layer behavior is understandable after testing, but not self-explanatory.

## 13. Top 10 Improvements

1. HIGH - Strengthen selected property summary into a trust summary.
Show the selected item's verification, evidence availability, audit activity, and Passport readiness more clearly before the drawer opens.

2. HIGH - Clarify the first-time workflow.
Make Map -> Property -> Passport -> Evidence -> Audit understandable through labels and hierarchy, not training.

3. HIGH - Reduce implementation language in primary UI surfaces before production.
Replace "v1 contracts," "synthetic internal preview," and similar implementation copy with product-safe internal wording when moving beyond preview.

4. HIGH - Rebalance map and table meaning.
Keep the table as explanation, but give the map stronger selected-location context so the map is not just a backdrop for table data.

5. MEDIUM - Rework Passport hierarchy.
Make verified fact, evidence, and review status more prominent than raw identity metadata. Move advanced identity fields behind progressive disclosure.

6. MEDIUM - Make Evidence less repetitive.
Merge or compress identity/provenance rows and highlight the support relationship to the fact.

7. MEDIUM - Translate Audit into reviewer accountability language.
Use user-facing event summaries, clearer actor/timestamp/status treatment, and less system-log phrasing.

8. MEDIUM - Clarify Layer Panel behavior.
Separate layers that filter records from layers that annotate records. Avoid making "Reports" sound like source-document access.

9. LOW - Give Context Bar slightly stronger presence on selection changes.
It should remain quiet, but users should notice that it explains current knowledge context.

10. LOW - Improve empty and unavailable state action language.
Keep the calm tone, but make reset/recovery actions more specific to the state: reset filters, restore layers, retry preview, or return to workspace.

## 14. Production Readiness Assessment

Can this preview serve as the UX blueprint for Falcon Intelligence?

Yes, with conditions. The current preview is strong enough to serve as the blueprint for the Intelligence Map workspace architecture and interaction model. It validates the key product thesis: Falcon Intelligence can preserve map/table context while progressively disclosing Passport, Evidence, and Audit trust surfaces.

It should not yet be treated as the final production UX. Before production UX signoff, the team should address:

- First-time workflow comprehension.
- Selected property trust summary.
- Drawer scan hierarchy.
- Layer behavior clarity.
- Production-safe copy.
- Responsive drawer/map/table behavior.
- Production accessibility audit.
- Real Falcon design-system integration.

The preview should proceed into V3 planning as a validated UX direction, not as a finished interface.

## Strengths

- Clear trust hierarchy: Map, Passport, Evidence, Audit.
- Strong preservation of workspace context through drawers.
- Calm, professional, non-AI-dashboard visual tone.
- Good internal keyboard and accessibility foundation.
- Honest handling of unavailable, stale, empty, permission, evidence, and audit states.
- Good use of table as structured explanation for map records.
- Strong fit with Falcon Intelligence's role as institutional knowledge, not automated judgment.

## Weaknesses

- Workflow is understandable but not yet self-explanatory to a new user.
- Map is spatially primary but table is semantically dominant.
- Selected summary under-explains the trust model before opening Passport.
- Drawer content is useful but not yet optimized for fast appraisal review.
- Context Bar is valuable but may be under-noticed.
- Layer Panel behavior may confuse filtering versus annotation.
- Some internal/synthetic implementation language remains prominent.

## Production UX Readiness

Status: conditionally ready as a UX blueprint; not ready as a final production UX.

The current preview is suitable for internal stakeholder review, V3 planning, and continued interaction refinement. It is not ready for customer-facing pilot use without additional UX passes for comprehension, copy, responsive behavior, production accessibility, and final Falcon design-system alignment.

## Recommendation For Beginning V3

Begin V3 if the goal is to deepen provenance, Passport, Evidence, and Audit contracts around the validated workspace model.

Do not begin V3 by adding new surfaces or expanding map features. The next work should strengthen the existing trust chain:

```text
Selected property
-> Passport trust summary
-> Evidence support
-> Audit accountability
```

V3 should treat the current preview as the interaction skeleton and improve the trust content model that flows through it. The highest-value next UX companion to V3 is a selected-property trust summary that makes the Passport/Evidence/Audit chain obvious before the user opens any drawer.
