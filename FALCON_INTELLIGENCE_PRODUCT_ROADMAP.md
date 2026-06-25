# Falcon Intelligence Product Roadmap

This is the canonical product planning document for Falcon Intelligence.

Falcon Intelligence is a premium Project Falcon knowledge module for appraisal firms. Falcon Core remains the operational platform for orders, assignments, users, workflow, delivery, and client-facing operations. Falcon Intelligence extends Falcon Core with internal-only firm knowledge, verified intelligence, provenance, evidence, audit, and future review workflows.

This roadmap does not authorize real appraisal data access, OneDrive access, report parsing, extraction, OCR, embeddings, model training, source-document preview, or ingestion. Real content work remains blocked until the production readiness gate and approval packet are completed.

## Product Vision

Falcon Intelligence turns a firm's verified appraisal work history into a trusted internal knowledge layer.

The product should help appraisers and reviewers answer:

- Have we worked on this property, borrower, client, market, or comparable before?
- What prior assignments, comps, leases, market indicators, or report references may be relevant?
- Why should this fact be trusted?
- Who verified it, when, and from what evidence?
- Can this intelligence be reused safely under firm policy?

The product is assistive. It surfaces internal knowledge with context, provenance, and guardrails. It must not create automatic valuation conclusions, silently select comps, bypass appraiser judgment, or expose internal intelligence to clients.

## Core Design Principles

- Falcon Core first: Falcon Core owns operational workflow; Falcon Intelligence plugs into it as a premium knowledge module.
- Local-first and tenant-first: firm data remains under firm control, tenant-scoped, permissioned, and auditable.
- Metadata before content: metadata-only workflows come before any content extraction, OCR, embeddings, or source preview.
- Verification before searchability: suggested facts do not become firm-searchable until approved.
- Provenance before trust: every surfaced fact must explain source, verification, review, confidence, freshness, and evidence.
- Appraiser judgment remains final: intelligence supports professional review, not valuation automation.
- Client visibility is blocked by default: internal intelligence, passports, evidence, audit, notes, and comp recommendations remain internal-only unless separately approved.
- Stable contracts before UI scale: schemas, snapshots, and synthetic contract tests protect Falcon integration from drift.
- Premium boundaries are explicit: advanced capabilities sit behind feature flags, permission gates, and production readiness gates.
- No cross-firm learning: one firm's data must not train, enrich, or search another firm's workspace.

## User Types

| User type | Primary needs | Key constraints |
| --- | --- | --- |
| Owner | Tenant policy, commercial controls, risk visibility, audit access, module enablement. | Must not bypass confidentiality, tenant isolation, or professional review. |
| Admin | User management, workflow configuration, folder and metadata policy, operational health. | Cannot convert unverified valuation facts into trusted intelligence. |
| Appraiser | Relevant prior assignments, comps, market indicators, passports, evidence, and reusable context. | Remains responsible for relevance, selection, verification, adjustment, and conclusions. |
| Reviewer | QA visibility, verification state, stale warnings, conflicts, audit trail, reviewer sign-off. | Must preserve traceability and professional independence. |
| Trainee | Supervised learning, limited assigned-work visibility, safe exposure to verified context. | Restricted from sensitive evidence and unsupervised reuse. |
| Client | Assignment-specific deliverables and status through Falcon Core. | No default access to internal Falcon Intelligence. |
| Falcon product/engineering | Stable contracts, tenant-safe integration points, observability, rollout controls. | Must not add real content pipelines without approved gates. |

## Product Philosophy

Falcon Intelligence should feel like a trusted internal memory, not a black-box answer engine.

The product should:

- Show why something surfaced.
- Make stale, incomplete, conflicting, or unreviewed data obvious.
- Keep high-risk actions deliberate and auditable.
- Prefer small trustworthy facts over broad unverified summaries.
- Keep UI surfaces dense, operational, and review-friendly.
- Make "open evidence" a permissioned provenance workflow, not a raw file browser.
- Make synthetic contract coverage the default until production gates pass.

The product should not:

- Train on report or client data by default.
- Mix data across firms.
- Expose client-confidential work product broadly.
- Generate final valuation language from unverified material.
- Treat a prior comp or conclusion as automatically reusable.
- Let convenience override auditability or approval policy.

## Roadmap V1-V10

### V1: Synthetic Contract Foundation

Goal: Establish safe, synthetic-only foundations for Falcon Intelligence.

Scope:

- Metadata scanner, manifests, search, assignment discovery, and profiles.
- Synthetic sample fixtures.
- Synthetic verified intelligence fixtures.
- Synthetic matcher for fake Falcon orders.
- Firm Intelligence Found card schema and CLI preview.
- Contract tests and smoke validation.

Success criteria:

- Full validation runs locally and in CI.
- No real reports, OneDrive data, source content, OCR, embeddings, vector stores, PDFs, DOCX, XLSX, CSV, TSV, or TXT exports are committed.
- Synthetic fixtures cover industrial, retail, office, purchase, lease-heavy, and work-in-progress assignments.
- Falcon card output is deterministic and covered by snapshots.

Production gate milestone:

- No real content gate opened.
- Metadata-only work and synthetic contract work only.

### V2: Falcon Card and Trust Contracts

Goal: Make the Firm Intelligence Found card usable as a stable Falcon integration target.

Scope:

- UI-facing card schema.
- Versioned card fixture snapshot.
- Falcon-style local card API envelope.
- Matcher groups for same subject, nearby assignments, property type, size, client, sale comps, lease comps, and market indicators.
- Match policy codes, warnings, recommended action codes, and audit event codes.

Success criteria:

- Falcon card schema has a versioned snapshot.
- API envelope has a versioned snapshot.
- Match groups include scores and explanations.
- Client/internal guardrails are documented.
- No report contents are read.

Production gate milestone:

- Still synthetic-only.
- Production API not authorized.

### V2A: Intelligence Workspace / Map Experience Specification

Goal: Establish the first canonical Falcon Intelligence Workspace UX, centered on Map as the primary Intelligence workspace.

Scope:

- Documentation-only Falcon Intelligence Workspace / Map Experience specification.
- Product positioning that keeps Falcon Core as the work-management platform and Falcon Intelligence as the premium institutional knowledge module.
- Future Falcon sidebar and Intelligence module navigation model.
- Canonical Map workspace layout with filter rail, large map canvas, synchronized bottom table, passport drawer, and nested evidence/audit drawers.
- Interaction model for filter, map, table, passport, evidence, and audit synchronization.
- Existing synthetic contract mapping from map workspace response, assignment profiles, Firm Intelligence Found card, passport drawer, evidence-open contract, audit events, permission policy, and schema registry to UI surfaces.
- Visual/brand principles that inherit the Falcon shell: calm, clean, operational, premium, trust-oriented, and not an "AI dashboard."

Success criteria:

- The UX model is documented in `docs/intelligence-workspace-map-experience.md`.
- The Map workspace is identified as the primary Intelligence workspace.
- Existing synthetic contracts remain the assumed UI data source.
- No new backend architecture, real extraction, OCR, embeddings, source-document preview, OneDrive access, production database/auth, or React UI is added.

Production gate milestone:

- Documentation-only.
- UI implementation and production map provider integration remain future work.
- Real data, source preview, extraction, OCR, embeddings, and production auth remain blocked by the existing gates.

### V2B: Intelligence Workspace State Model

Goal: Define trustworthy bad-state behavior for the Falcon Intelligence Map workspace before UI implementation.

Scope:

- Documentation-only state model for empty, loading, permission denied, stale, no-results, evidence unavailable, audit unavailable, future AI suggestion pending, future reviewer approval pending, and error states.
- State priority order for workspace and nested drawer states.
- Calm, professional copy guidance that avoids magical AI language and avoids implying valuation conclusions.
- Contract mapping from Permission Policy, Map Workspace Contract, Evidence Open Contract, Evidence Link Model, Audit Event Model, Assignment Profiles, Manifest Search, and Schema Registry/Changelog to UI states.
- Falcon shell alignment for state visuals: restrained, operational, no gimmicky AI visuals, and no wall-of-cards fallback pages.

Success criteria:

- The state model is documented in `docs/intelligence-workspace-state-model.md`.
- Bad states explain what is unavailable, why it matters, and what actions remain available without leaking restricted facts.
- Existing synthetic contracts remain the assumed state inputs.
- No new schemas, React UI, backend architecture, real extraction, OCR, embeddings, source-document preview, OneDrive access, production database/auth, or production map provider work is added.

Production gate milestone:

- Documentation-only.
- Production UI implementation, production map provider integration, source preview, real extraction, OCR, embeddings, production auth, and production database work remain blocked by existing gates.

### V2C: Falcon Shell Integration / Design System Extension

Goal: Define how Falcon Intelligence extends the Falcon shell and design system before UI implementation.

Scope:

- Documentation-only Falcon shell integration and design-system extension specification.
- Falcon Intelligence UX Commandments as non-negotiable UI principles.
- Shell alignment for inherited sidebar, top navigation behavior, workspace labels, restrained visual system, and no wall-of-cards dashboard pattern.
- Component reuse, extension, and new component matrix for navigation, sidebar, cards, tables, drawers, search, status badges, map canvas, layer panel, property marker, and context bar.
- Canonical visual hierarchy from Falcon Shell through Passport, Evidence, and Audit surfaces.
- Future Context Bar concept for plain-language knowledge context across map, table, passport, evidence, and audit selection.

Success criteria:

- The shell integration specification is documented in `docs/intelligence-workspace-falcon-shell-integration.md`.
- Falcon Intelligence is explicitly positioned as a premium module inside Falcon, not a separate product.
- Reuse/extend/new component boundaries are documented before UI build.
- No new schemas, React UI, backend architecture, real extraction, OCR, embeddings, source-document preview, OneDrive access, production database/auth, or production map provider work is added.

Production gate milestone:

- Documentation-only.
- Production UI implementation, production map provider integration, source preview, real extraction, OCR, embeddings, production auth, and production database work remain blocked by existing gates.

### V2D: React Readiness & Contract Gap Review

Goal: Prove that the first Falcon Intelligence React workspace can be built from existing v1 synthetic contracts.

Scope:

- Documentation-only React readiness and contract gap review.
- Inventory of current v1 contracts and snapshots that support React UI work.
- UI readiness matrix using `READY`, `DERIVED`, and `DEFERRED` statuses.
- Potential gap review with a preference for derived UI composition over schema expansion.
- Recommended React build order from Falcon shell integration through production data replacement as future work.
- Architecture assessment for whether React can begin without additional backend work.

Success criteria:

- The review is documented in `docs/react-readiness-contract-gap-review.md`.
- Existing v1 contracts are assessed as sufficient for the first internal React workspace preview.
- No required schema changes are identified unless truly unavoidable.
- No React UI, map rendering, schema changes, contract changes, backend architecture, real extraction, OCR, embeddings, source-document preview, OneDrive access, production auth/database, or production map provider work is added.

Production gate milestone:

- Documentation-only.
- Production UI implementation, production map provider integration, source preview, real extraction, OCR, embeddings, production auth, and production database work remain blocked by existing gates.

### V2E: Vertical Slice #1: Synchronized Workspace

Goal: Build the first minimal internal React preview proving map marker, table row, and selected property summary synchronization.

Scope:

- Falcon-like shell framing.
- Intelligence workspace page.
- Workspace header.
- Left filter rail shell.
- Synthetic coordinate-plane map placeholder using existing v1 synthetic map workspace data.
- Bottom synchronized table.
- Compact selected property summary.
- Single-source-of-truth React selection state.
- Tests proving render, marker rendering, table row rendering, marker-to-table selection, table-to-marker selection, and summary updates.

Success criteria:

- Markers render from existing synthetic v1 data.
- Table rows render from matching synthetic v1 data.
- Clicking a marker selects the matching table row and updates the selected property summary.
- Clicking a table row selects the matching marker and updates the selected property summary.
- Selected marker and selected row have visible selected states.
- No new schemas, backend architecture, production map provider, production auth/database, source preview, real extraction, OCR, embeddings, or OneDrive access is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local data only.
- No production map provider, source preview, production auth, production database, extraction, OCR, embeddings, or real data work is authorized.

### V2F: Passport Drawer Preview

Goal: Extend the internal React workspace preview so the selected property can open a right-side Passport drawer without losing map/table context.

Scope:

- Open a Passport drawer from the selected property summary when the selected row has a synthetic `passport_id`.
- Render Passport identity, verified fact summary, confidence/provenance language, evidence metadata summary, verification/review fields, and related assignment context.
- Preserve selected marker, selected table row, and selected property summary while the drawer is open.
- Close the drawer without clearing or changing the current map/table selection.
- Use existing v1 synthetic passport drawer, data passport, verified intelligence, and map workspace snapshots only.
- Tests proving drawer open, selected-context preservation, drawer close, and selection preservation.

Success criteria:

- Map/table selection still controls the selected property summary.
- Opening the Passport drawer does not navigate away from the workspace or hide the selected marker/table row context.
- Closing the Passport drawer returns to the same selected property.
- Evidence and audit detail remain deferred.
- No new schemas, backend architecture, production map provider, production auth/database, source preview, real extraction, OCR, embeddings, or OneDrive access is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local data only.
- Passport drawer content is metadata-only and does not open source documents.
- Evidence drawer, audit drawer, production auth, production database, source preview, extraction, OCR, embeddings, and real data work remain blocked.

### V2G: Evidence Drawer Preview

Goal: Extend the internal React workspace preview so evidence metadata can open from the Passport drawer without losing Passport, map, table, or selected property context.

Scope:

- Open a nested/right-side Evidence drawer from an evidence row/action inside the Passport drawer.
- Render evidence title/type, source/report identifier, provenance metadata, permission/open status, confidence or verification context, and metadata-only unavailable language.
- Use the existing metadata-only Evidence Link Model and Evidence Open Contract.
- Preserve selected marker, selected table row, selected property summary, and Passport drawer context while Evidence is open.
- Close Evidence back to Passport without clearing workspace selection.
- Tests proving workspace render, Passport open, Evidence open, Evidence close, and selection preservation.

Success criteria:

- Passport remains open while Evidence is open.
- Closing Evidence returns to the same Passport context.
- Map marker, table row, and selected summary remain selected throughout.
- Evidence drawer makes clear that source documents, OCR, extraction, and previews are unavailable.
- Audit handoff is shown only as existing contract metadata; the Audit Timeline drawer is deferred.
- No new schemas, backend architecture, production map provider, production auth/database, source preview, real extraction, OCR, embeddings, OneDrive access, or real file access is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local data only.
- Evidence drawer content is metadata-only and does not open source documents.
- Audit drawer, production auth, production database, source preview, extraction, OCR, embeddings, OneDrive, and real data work remain blocked.

### V2H: Audit Timeline Drawer Preview

Goal: Extend the internal React workspace preview so audit timeline metadata can open from Evidence without losing Evidence, Passport, map, table, or selected property context.

Scope:

- Open a nested Audit drawer from Evidence when existing evidence-open metadata supports an audit handoff.
- Render matching synthetic audit event snapshots as timeline rows.
- Show fact/evidence context, event type, actor identity, timestamp, action summary, verification/searchability status, and provenance context when present in existing fixtures.
- Show plain unavailable language when no matching audit event snapshot exists.
- Preserve selected marker, selected table row, selected property summary, Passport drawer, and Evidence drawer while Audit is open.
- Close Audit back to Evidence, close Evidence back to Passport, and close Passport while clearing nested Evidence/Audit state safely.
- Tests proving workspace render, Passport open, Evidence open, Audit open, drawer close behavior, parent cleanup, and selection preservation.

Success criteria:

- Audit opens from Evidence without closing Evidence or Passport.
- Closing Audit returns to the same Evidence context.
- Closing Evidence returns to the same Passport context.
- Closing Passport clears nested drawer state without changing workspace selection.
- Audit rows use existing synthetic audit event fixtures only and do not imply production audit certainty.
- No new schemas, real audit backend, production auth/database, source preview, real extraction, OCR, embeddings, OneDrive access, real files, or production map provider work is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local data only.
- Audit drawer content is fixture-backed metadata only and is not production audit history.
- Production audit persistence, auth, database, source preview, extraction, OCR, embeddings, OneDrive, and real data work remain blocked.

### V2I: Workspace State Rendering Preview

Goal: Render the canonical workspace and nested drawer states from the V2B state model inside the internal React preview.

Scope:

- Add a clearly labeled preview-only state simulator for internal inspection.
- Render loading, empty, permission denied, stale data, no results, evidence unavailable, audit unavailable, and generic error states.
- Preserve state priority from the V2B state model: permission denied, error, loading, empty, stale, no results, content available.
- Keep state copy calm, operational, and Falcon-aligned.
- Disable workspace interactions when state requires unavailable or restricted behavior.
- Keep stale data usable with a visible banner.
- Render evidence unavailable and audit unavailable states through the existing nested drawer flow.
- Tests proving each state renders and the existing happy path still works.

Success criteria:

- No fake results, fake confidence, stack traces, or production diagnostics appear in preview states.
- Permission denied does not show property markers or table rows.
- Stale data keeps content usable while warning the user.
- No-results and error states include a simple reset path.
- Evidence unavailable and audit unavailable use metadata-only language and do not open source previews.
- No backend state service, real permission backend, production auth/database, schema change, real extraction, OCR, embeddings, OneDrive access, source preview, real files, or production map provider work is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local state simulation only.
- Production state services, auth, database, source preview, extraction, OCR, embeddings, OneDrive, real data, and real file access remain blocked.

### V2J: Context Bar Preview

Goal: Add the Falcon Intelligence Context Bar concept from V2C into the internal React workspace preview.

Scope:

- Add a compact Context Bar below the workspace header.
- Derive plain-language context from current local UI state and existing synthetic contracts.
- Update the Context Bar for workspace/map view, selected property, Passport open, Evidence open, Audit open, and workspace state simulator states.
- Keep the Context Bar distinct from breadcrumbs; it explains current knowledge context rather than navigation path.
- Use conservative fallback language when fields are missing.
- Tests proving default workspace context, selected property context, Passport context, Evidence context, Audit context, and workspace state context.

Success criteria:

- Context Bar remains compact, calm, Falcon-like, and useful.
- Context text updates as selection and nested drawers change.
- State contexts cover loading, empty, permission denied, stale, no-results, evidence unavailable, audit unavailable, and error states.
- Context text does not invent facts, reviewer approval, source access, production diagnostics, or valuation conclusions.
- No new schemas, backend architecture, production map provider, production auth/database, source preview, real extraction, OCR, embeddings, OneDrive access, or real file access is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local derived context only.
- Production context services, auth, database, source preview, extraction, OCR, embeddings, OneDrive, real data, and real file access remain blocked.

### V2K: Layer Panel Preview

Goal: Add the first preview-only Layer Panel to the internal React workspace so users can toggle synthetic workspace layers while preserving map/table synchronization.

Scope:

- Add a compact Falcon-like Layer Panel near the synthetic map workspace.
- Support preview toggles for Subjects, Verified Knowledge, Reports, Evidence Available, and Reviewer/Audit Activity.
- Display future/deferred layers as disabled controls: Sales, Leases, Market Areas, Comparable Clusters, and AI Suggestions.
- Use derived local UI state from existing v1 synthetic map workspace, passport, evidence, and audit metadata only.
- Let the Subjects layer hide/show visible markers and synchronized table rows.
- Let derived layers update visible badges/details without introducing production filters or GIS behavior.
- Show calm layer-filtered workspace language when no records are visible under active layer settings.
- Preserve existing Passport, Evidence, Audit, Context Bar, and workspace state preview behavior.
- Tests proving layer panel render, marker/table visibility changes, derived badge changes, selected-hidden messaging, Context Bar layer state, and existing drawer happy path preservation.

Success criteria:

- Layer toggles affect visible markers, table rows, or derived badges without schema changes.
- Hidden selected-property context is handled calmly without implying data loss or production filtering.
- Context Bar reflects the layer-filtered/no-visible-data state.
- Preview-only state simulator remains distinct from the production-like layer controls.
- No new schemas, backend architecture, production map provider, real GIS calculations, search, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, or real file access is added.

Production gate milestone:

- Internal React preview only.
- Synthetic/local layer behavior only.
- Production map layers, GIS providers, backend filters, search, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, and real file access remain blocked.

### V2L: Accessibility and Keyboard Navigation Pass

Goal: Improve accessibility semantics and keyboard navigation in the internal React workspace preview without expanding product scope.

Scope:

- Make synthetic map markers keyboard focusable and selectable through native button behavior.
- Make synchronized table rows keyboard focusable and selectable with Enter or Space.
- Keep layer toggles as accessible labeled controls with explanatory descriptions.
- Keep the preview-only state simulator clearly labeled as an internal preview control.
- Add accessible Context Bar status semantics.
- Upgrade Passport, Evidence, and Audit drawers to labeled non-modal dialog semantics while preserving visible map/table context.
- Add sensible focus handling when opening and closing Passport, Evidence, and Audit drawers.
- Add Escape handling that closes the deepest open drawer first: Audit, then Evidence, then Passport.
- Preserve selected marker, table row, and selected property summary while opening or closing drawers.
- Tests proving keyboard marker selection, keyboard table-row selection, Escape close order, disabled Passport action behavior, layer toggle labels, Context Bar labeling, and existing happy path behavior.

Success criteria:

- Tab can reach preview controls, layer controls, markers, table rows, selected property actions, and drawer controls.
- Enter or Space selects focused markers and table rows.
- Enter or Space activates Passport, Evidence, Audit, and close controls through native button behavior.
- Escape closes nested drawers in the correct order without changing selected property context.
- Disabled/unavailable Passport action remains non-activatable and communicates why it is unavailable.
- No new product features, visual redesign, schema changes, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, or real file access is added.

Production gate milestone:

- Internal React preview only.
- Accessibility behavior is local UI behavior only.
- Production accessibility audit, production auth, production database, source preview, extraction, OCR, embeddings, OneDrive, real data, and production map provider work remain blocked.

### V2M: Visual Polish and Falcon Shell Alignment Pass

Goal: Refine the internal React preview so it feels more like a premium Falcon module while preserving V2E-V2L behavior.

Scope:

- Refine shell, header, navigation, spacing, borders, typography, and hierarchy.
- Improve Context Bar presentation as a compact Falcon knowledge-context surface.
- Improve filter rail and Layer Panel readability without changing layer behavior.
- Improve synthetic coordinate-plane framing while keeping the map as the primary workspace.
- Improve marker and selected-marker treatment without adding map provider behavior.
- Improve bottom table density, hover affordance, and selected-row treatment.
- Improve selected property summary density and alignment.
- Improve Passport, Evidence, and Audit drawer hierarchy so trust and traceability surfaces read clearly.
- Keep the preview calm, professional, appraisal-platform appropriate, and visibly separate from gimmicky AI dashboard styling.

Success criteria:

- Existing V2E-V2L interactions and tests continue passing.
- The UI feels more like an extension of the Falcon shell and less like a standalone prototype.
- Visual hierarchy reinforces the product model: map primary, table explanatory, drawers contextual, state simulator preview-only.
- No product redesign, new features, schema changes, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, or real file access is added.

Production gate milestone:

- Internal React preview only.
- Visual polish is CSS/local UI composition only.
- Production design-system integration, production map provider, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, and real file access remain blocked.

### V3A: Knowledge Summary Trust Panel

Goal: Reframe the selected property summary into a Knowledge Summary panel that makes the core trust workflow clear before a user opens Passport, Evidence, or Audit drawers.

Scope:

- Rename and reframe the selected property summary as Knowledge Summary.
- Surface the selected property identity, address, property use, trust status, verified fact count, evidence count, audit activity status, and last review/verification metadata where existing fixtures support it.
- Add plain-language trust and next-step copy that explains what is known and why the Passport should be opened.
- Keep marker selection, table selection, Context Bar behavior, Passport drawer, Evidence drawer, and Audit drawer interactions intact.
- Derive all indicators from existing synthetic map workspace, passport, evidence, and audit metadata.

Success criteria:

- Selecting a marker updates the Knowledge Summary.
- Selecting a table row updates the Knowledge Summary.
- The panel shows verified facts, evidence, audit/reviewer activity indicators, and conservative trust language.
- Open Passport behavior still preserves map/table selection and nested drawer behavior.
- Hidden or unavailable selected-property states remain calm and non-actionable.
- No new schemas, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, new product surfaces, or broad redesign is added.

Production gate milestone:

- Internal React preview only.
- Knowledge Summary is derived local presentation only and is not a production trust score, production reviewer approval system, production auth check, or source-document access surface.
- Production design-system integration, production map provider, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, and real file access remain blocked.

### V3B: First-Time Workflow Guidance

Goal: Make the Falcon Intelligence trust chain self-explanatory at first glance without adding a modal tutorial or new product surface.

Scope:

- Add lightweight, dismissible first-time guidance for the workflow: Map, Property, Knowledge Summary, Passport, Evidence, Audit.
- Hide or reduce guidance after the user explicitly selects a property from the map or table.
- Keep guidance out of loading, permission denied, error, and other inappropriate unavailable states.
- Add Knowledge Summary next-step copy that directs the user to Passport for verified facts, evidence, and audit history.
- Add subtle Passport and Evidence drawer hints explaining that Evidence supports trust and Audit shows review/verification history.
- Keep dismissal local to the current preview session only.

Success criteria:

- Initial guidance appears before the user explicitly selects a property.
- Selecting a marker or table row hides the initial guidance.
- Dismissing guidance hides it for the current preview session.
- Knowledge Summary, Passport, and Evidence guidance remains plain, professional, and non-blocking.
- Existing map/table selection, Passport, Evidence, Audit, layers, state simulator, Context Bar, accessibility, and keyboard behavior continue passing.
- No new schemas, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, new product surfaces, or broad redesign is added.

Production gate milestone:

- Internal React preview only.
- Guidance is local UI state only and does not persist to backend storage.
- Production onboarding, telemetry, design-system integration, production map provider, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, and real file access remain blocked.

### V3C: Passport Information Architecture Pass

Goal: Improve the Passport drawer's information architecture so it is easier to scan and clearly supports the trust chain from Property to Knowledge Summary to Passport to Evidence to Audit.

Scope:

- Reorganize existing Passport drawer content into clearer sections: Identity, Verified Knowledge, Evidence, Verification / Review, and Related Work.
- Move property context, property use, record type, assignment, passport, and tenant identifiers into Identity.
- Combine verified fact, confidence/status language, and confidence dimensions into Verified Knowledge.
- Keep Evidence actions easy to find and preserve the metadata-only evidence guidance.
- Keep verification, review, and audit event metadata together in Verification / Review.
- Move related assignment/report context to Related Work.
- Use existing synthetic map, passport, evidence, and audit metadata only.

Success criteria:

- Passport sections render with clear headings and expected property context.
- Verified Knowledge presents existing fact/status/confidence metadata without implying production conclusions.
- Evidence opens from Passport exactly as before.
- Evidence still opens Audit exactly as before.
- Opening, closing, keyboard, Escape, Context Bar, first-time guidance, map selection, table selection, and Knowledge Summary behavior remain intact.
- No new schemas, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, new product surfaces, or broad redesign is added.

Production gate milestone:

- Internal React preview only.
- Passport IA is local UI composition over existing synthetic contracts.
- Production design-system integration, production map provider, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, and real file access remain blocked.

### V3D: Evidence Readability Pass

Goal: Improve the Evidence drawer's scan hierarchy while preserving metadata-only behavior and existing Evidence-to-Audit interactions.

Scope:

- Reorganize existing Evidence drawer presentation into Evidence Summary, Source Metadata, Trust Context, and Audit Handoff sections.
- Surface evidence title/type, source/report identifier, open status, and a concise explanation that the metadata supports the selected knowledge record.
- Keep provenance and source metadata fields together without implying source document access.
- Keep confidence/verification context in a dedicated Trust Context section with conservative metadata-only language.
- Keep the Open Audit action clear when audit handoff metadata is available and disabled/unavailable when it is not.
- Use existing synthetic evidence, passport, and audit metadata only.

Success criteria:

- Evidence Summary, Source Metadata, Trust Context, and Audit Handoff sections render clearly.
- Evidence unavailable state still renders with metadata-only language.
- Passport to Evidence to Audit happy path continues to pass.
- Context Bar, keyboard, Escape, Passport close, Evidence close, and Audit close behavior remain intact.
- No new schemas, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, new product surfaces, or broad redesign is added.

Production gate milestone:

- Internal React preview only.
- Evidence readability is local UI composition over existing metadata-only synthetic contracts.
- Source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, real file access, production map provider, and backend work remain blocked.

### V3E: Audit Timeline Pass

Goal: Transform the Audit drawer into a readable chronological timeline using the existing synthetic Audit Event Model.

Scope:

- Reorganize the Audit drawer into Timeline Summary, Chronological Timeline, and Current Status sections.
- Present audit events as actor, action, timestamp, and result so users can answer who changed knowledge, when, and what happened.
- Sort matching synthetic audit events by existing timestamp where possible while preserving synthetic placeholder timestamps without inventing real dates.
- Show total events, current verification status, last activity, and additional audit history availability with conservative language.
- Preserve unavailable audit behavior when no synthetic audit events are available.
- Use existing synthetic audit, evidence, passport, and map metadata only.

Success criteria:

- Timeline Summary renders total events and current verification status.
- Chronological Timeline renders existing synthetic events as readable actor/action/timestamp/result rows.
- Current Status renders verification state, last activity, and additional audit history availability.
- Audit unavailable state remains explicit without inventing history.
- Passport to Evidence to Audit happy path continues to pass.
- Context Bar, keyboard, Escape, Passport close, Evidence close, and Audit close behavior remain intact.
- No new schemas, backend architecture, production audit services, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, new product surfaces, or broad redesign is added.

Production gate milestone:

- Internal React preview only.
- Audit timeline presentation is local UI composition over existing synthetic audit events.
- Production audit persistence, production audit services, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, real data, real file access, production map provider, and backend work remain blocked.

### V3G: Guided Stakeholder Review Packet

Goal: Prepare a guided documentation-only review packet so appraisers, reviewers, owners, and admins can evaluate the current internal preview for comprehension, trust, and workflow value.

Scope:

- Stakeholder review purpose and synthetic-preview framing.
- Non-goals disclaimer for real reports, OCR, extraction, OneDrive, production database/auth, source document preview, production map provider, and real data.
- Guided demo script for Map, Knowledge Summary, Passport, Evidence, Audit Timeline, drawer closing, layers, and optional state previews.
- Role-specific questions for appraisers, reviewers, owners, and admins.
- Observation checklist for comprehension, hesitation, context recovery, terminology, and perceived value.
- Pass/fail criteria before V4 planning or implementation expansion.
- Feedback capture template for stakeholder notes and go/no-go recommendations.
- Recommended next decision paths after review.

Success criteria:

- The packet is documented in `docs/stakeholder-review-packet-v3.md`.
- Reviewers can run a guided session without presenting the preview as production-ready.
- The packet keeps all current data and production-readiness boundaries explicit.
- No UI changes, code changes, schemas, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, new product surfaces, or broad redesign is added.

Production gate milestone:

- Documentation-only.
- Stakeholder review does not authorize production data, real reports, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, or backend work.

### V3H: Synthetic Dataset Expansion and Demo Scenario

Goal: Expand the internal preview's synthetic dataset so the Map workspace feels more reviewable and appraiser-realistic without changing v1 contract shapes.

Scope:

- Add synthetic Map workspace records for a reviewable airport warehouse demo scenario, unverified property, evidence/no-evidence states, audit/no-audit states, multiple property types, multiple statuses, and meaningful layer/table behavior.
- Keep all records local and synthetic.
- Regenerate the v1 Map Workspace UI snapshot from the existing serializer.
- Add a focused frontend demo scenario test: "Find the warehouse near the airport and verify why we trust its building area."
- Update map workspace contract tests and smoke checks for the expanded fixture counts.

Success criteria:

- The preview includes verified and unverified synthetic records.
- The preview includes industrial, retail, and office records.
- The preview includes evidence-available and no-evidence records.
- The preview includes audit-available and audit-unavailable records.
- The airport warehouse scenario can move through Knowledge Summary, Passport, Evidence, and Audit using existing v1 contract shapes.
- No new schemas, backend architecture, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, real client data, real reports, or broad redesign is added.

Production gate milestone:

- Internal synthetic preview only.
- Expanded dataset does not authorize real data, report content, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, or backend work.

### V3I: Realistic Filter/Search Preview

Goal: Make the expanded synthetic Map workspace easier to explore with local search and filters while preserving map/table/Knowledge Summary synchronization.

Scope:

- Add local search across synthetic property label, address, city, property type, record type, status, and verification status.
- Add local filter controls for property type, verification status, evidence availability, audit activity, and record status.
- Keep filters derived from existing synthetic v1 snapshot data.
- Keep Layer Panel behavior separate from search/filter behavior.
- Preserve synchronized markers, table rows, Knowledge Summary, Passport, Evidence, and Audit behavior.
- Show calm unavailable messaging when filters hide the selected property.
- Support the airport warehouse demo scenario through search for "airport" and combined industrial/verified/evidence filters.

Success criteria:

- Searching for "airport" reveals the airport warehouse record.
- Local filters narrow visible rows and markers.
- Reset filters restores the full synthetic workspace.
- Hidden selected property behavior remains calm and non-destructive.
- Passport to Evidence to Audit happy path continues to pass.
- No new schemas, backend architecture, production search service, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, real client data, real reports, or broad redesign is added.

Production gate milestone:

- Internal synthetic preview only.
- Search/filter behavior is local UI state only and does not authorize production search, embeddings, backend filtering, real data, source preview, extraction, OCR, OneDrive, production auth, production database, or production map provider work.

### V3J: Demo Readiness Review

Goal: Evaluate whether the current internal preview is ready for a guided internal demo using the synthetic airport warehouse scenario after V3I.

Scope:

- Documentation-only demo readiness review.
- Assess first impression, search for "airport", filter usefulness, map/table clarity, Knowledge Summary, Passport, Evidence, Audit Timeline, state simulator, Layer Panel, and synthetic limitations.
- Determine whether the preview is ready to show Mike, Pam, and Abby as a guided preview.
- Identify likely stakeholder questions, risks of demoing too early, top fixes before demo, and go/no-go recommendation.
- Recommend either V3K Demo Script Polish / Stakeholder Review Prep or pausing development to run the guided review.

Success criteria:

- The review is documented in `docs/demo-readiness-review-v3.md`.
- The airport warehouse scenario has a clear guided demo script.
- The review distinguishes guided demo readiness from production readiness.
- Synthetic/local limitations remain explicit.
- No UI changes, code changes, schemas, backend architecture, production search service, production map provider, source preview, real extraction, OCR, embeddings, OneDrive access, production auth/database, real client data, real reports, or broad redesign is added.

Production gate milestone:

- Documentation-only.
- Demo readiness does not authorize production data, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, backend work, or production search.

### V3.5A: Spatial Continuity Pass

Goal: Strengthen the feeling that Passport, Evidence, and Audit are expansions of the currently selected property rather than independent floating panels.

Scope:

- Improve drawer anchoring, spacing, overlay treatment, and subtle CSS-only transitions/continuity treatment where appropriate.
- Keep the selected marker, selected table row, and Knowledge Summary visually persistent while drawers are open.
- Add layout state classes that allow the workspace to visually acknowledge open Passport, Evidence, and Audit drawers without changing data flow or behavior.
- Preserve existing synchronized map/table/Knowledge Summary, Passport, Evidence, Audit, search/filter, layer, state, accessibility, and keyboard behavior.

Success criteria:

- Opening Passport, Evidence, or Audit makes the selected property feel visually anchored in the underlying workspace.
- Nested drawers read as progressive detail expansions of the same selected property.
- No workflow, data, contract, schema, backend, or production map behavior changes are added.
- Existing tests and validation continue passing.

Production gate milestone:

- Internal React preview styling pass only.
- Spatial continuity styling does not authorize production map provider work, source preview, extraction, OCR, embeddings, OneDrive access, production auth/database, real data, schema changes, backend architecture, or new product features.

### V3.5B: Visual Rhythm Pass

Goal: Improve spacing, section rhythm, typography hierarchy, divider consistency, and visual breathing room across the internal preview without expanding scope.

Scope:

- Refine Falcon shell spacing and hierarchy.
- Improve Workspace header, Context Bar, guidance, and preview-only simulator rhythm.
- Tighten filter/search controls and Layer Panel spacing without changing controls.
- Improve Map frame rhythm and marker/table relationship.
- Improve Knowledge Summary spacing, metric grouping, and selected-row readability.
- Refine Passport, Evidence, and Audit drawer section spacing, dividers, and timeline cadence.
- Keep all changes visual-only.

Success criteria:

- The preview feels calmer, more readable, and more professional without becoming oversized or flashy.
- Existing interactions, labels, DOM structure, tests, and data behavior remain intact.
- No new UI surfaces, features, schemas, backend behavior, data changes, production map provider, source preview, extraction, OCR, embeddings, OneDrive access, production auth/database, or real data work is added.

Production gate milestone:

- Internal React preview styling pass only.
- Visual rhythm refinement does not authorize production UI integration, production design-system migration, backend work, schema changes, real data access, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or production map provider work.

### V3.5C: Language Audit

Goal: Refine visible UI language so Falcon Intelligence reads like a professional appraisal knowledge system rather than an engineering prototype.

Scope:

- Review and refine visible copy in the Workspace header, Context Bar, first-time guidance, search/filter labels, Layer Panel, Knowledge Summary, Passport, Evidence, Audit/Review History, workspace state messages, buttons, badges, status labels, and preview-only simulator labels.
- Prefer appraiser-natural language such as "supporting evidence" and "review history" where accurate.
- Keep synthetic/preview limitations explicit without overloading the interface with engineering language.
- Avoid magical AI language, production claims, source-access claims, reviewer-approval claims, and valuation conclusions.
- Preserve all behavior, interactions, contracts, data, and UI surfaces.

Success criteria:

- UI copy is calmer, more professional, and easier for appraisers/reviewers to understand.
- Supporting evidence and review history language replaces awkward metadata/audit phrasing where appropriate.
- Preview and synthetic limitations remain honest and defensible.
- Tests are updated only where exact copy assertions changed.
- No features, schemas, backend behavior, data changes, new UI surfaces, production map provider, source preview, extraction, OCR, embeddings, OneDrive access, production auth/database, or real data work is added.

Production gate milestone:

- Internal React preview copy pass only.
- Language refinement does not authorize production copy approval, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, backend work, schema changes, or real data access.

### V3.5D: Interaction Consistency Pass

Goal: Align repeated interaction patterns across the internal preview so selection, drawers, buttons, filters, layer toggles, status language, and keyboard behavior feel like one coherent Falcon product.

Scope:

- Refine visible interaction terminology around Knowledge Summary, Passport, supporting evidence, and review history.
- Align drawer close controls, section headings, unavailable language, and nested drawer status copy.
- Keep filter, layer, and empty-table reset behavior predictable when records disappear from the current view.
- Improve subtle hover and disabled feedback for reset controls, layer toggles, drawer controls, supporting evidence actions, and primary actions.
- Preserve synchronized map/table/property selection, Passport, supporting evidence, review history, filters, layers, state simulator, Context Bar, and keyboard/Escape behavior.

Success criteria:

- Map markers, table rows, Knowledge Summary, Passport, supporting evidence, and review history consistently communicate that the user is still working on the selected property.
- Repeated actions use consistent labels and accessible names.
- Supporting evidence and review history terminology remains consistent across buttons, metrics, drawers, state labels, and tests.
- No features, schemas, backend behavior, data changes, production map provider, source preview, extraction, OCR, embeddings, OneDrive access, production auth/database, or real data work is added.

Production gate milestone:

- Internal React preview interaction-consistency pass only.
- This pass does not authorize production interaction design approval, backend work, schema changes, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, or real data access.

### V3.5E: Workspace Cohesion Review

Goal: Evaluate whether the Falcon Intelligence preview now feels like one coherent professional application after the V3.5 refinement passes.

Scope:

- Documentation-only review of the complete Search / Filters to Map to Knowledge Summary to Passport to Supporting Evidence to Review History workflow.
- Assess product identity, workflow cohesion, visual cohesion, interaction cohesion, language cohesion, trust-chain clarity, remaining UX debt, production UX readiness, and next recommendation.
- Determine whether the preview is internally coherent, suitable for guided stakeholder review, and stable enough to serve as a V4 UX blueprint.

Success criteria:

- The review is documented in `docs/workspace-cohesion-review-v3_5.md`.
- Remaining UX debt is separated from intentionally blocked future capabilities.
- Recommendation is explicit: workspace foundation complete, proceed to V4 planning after stakeholder review.
- No UI changes, code changes, features, schemas, backend behavior, production architecture, production map provider, source preview, extraction, OCR, embeddings, OneDrive access, production auth/database, or real data work is added.

Production gate milestone:

- Documentation-only review checkpoint.
- This review does not authorize production UX approval, backend work, schema changes, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, or real data access.

### V3.5F: Layout De-Clutter / Mockup Alignment Pass

Goal: Refactor the internal preview layout so the workspace feels more spacious, aligned, and professional while preserving all existing behavior.

Scope:

- Move the Layer Panel out of the map overlay and into a stable right-side workspace rail.
- Arrange the main workspace into a clean grid: Filters card, Map card above Assignments/Intelligence table, and Layers card above Knowledge Summary.
- Preserve the dark Falcon sidebar, top workspace header, Context Bar, first-time guidance banner, preview-only state simulator, map/table synchronization, search/filter behavior, layer toggles, Knowledge Summary, Passport, Supporting Evidence, Review History, and keyboard/Escape behavior.
- Refine CSS spacing, card boundaries, gutters, map/table proportion, and right-rail hierarchy to better match the clean mockup direction.

Success criteria:

- The Layer Panel no longer floats over the map or map markers.
- Filters and layers are separated into stable side cards.
- The map remains visually larger and more primary than the table.
- The table remains readable without dominating the workspace.
- Existing happy path, search/filter behavior, layer behavior, nested drawer flow, keyboard behavior, frontend tests, and build continue passing.
- No product features, schemas, backend behavior, data changes, production map provider, source preview, extraction, OCR, embeddings, OneDrive access, production auth/database, or real data work is added.

Production gate milestone:

- Internal React preview layout/CSS pass only.
- This pass does not authorize production UI approval, backend work, schema changes, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, or real data access.

### V3: Provenance, Passport, and Evidence Contracts

Goal: Explain why surfaced facts should be trusted.

Scope:

- Evidence link model.
- Data passport model.
- Passport detail lookup.
- Passport detail drawer schema and snapshot.
- Evidence-open contract.
- Confidence dimensions and provenance docs.
- Top match passport summaries on the card.

Success criteria:

- Card top-match `passport_id` resolves to full passport detail.
- Passport detail drawer has a stable v1 snapshot.
- Evidence-open response returns metadata-only summaries and suggested audit payloads.
- No source files are opened.

Production gate milestone:

- Source-document preview remains blocked.
- Evidence links are placeholders only.

### V4: Permissions and Audit Contracts

Goal: Prove internal-only behavior, role boundaries, and audit handoff in local contracts.

Scope:

- Local permission policy scaffold.
- Permission-aware Falcon contract tests.
- Audit event builders.
- Historical comparable justification model.
- Audit event envelope snapshots.
- End-to-end synthetic workflow from card to passport to evidence.

Success criteria:

- Client role is denied internal intelligence.
- Trainee access is limited.
- Evidence access levels are respected.
- Suggested audit payloads are covered by snapshots.
- Historical comp reuse creates justification and audit payload.

Production gate milestone:

- Production auth and audit persistence are not implemented.
- Future production Falcon must enforce real tenant membership, order access, and durable audit storage.

### V5: Intelligence Map Workspace Contract

Goal: Define a spatial/table workspace for exploring orders, assignments, comps, and verified intelligence.

Scope:

- Synthetic map record model.
- Filterable map/table serializer.
- Synthetic fixture for active order, completed assignment, sale comp, lease comp, historical comp, and current subject.
- Versioned synthetic UI response snapshot for the map workspace.
- Documentation-only UI concept with sidebar filters, table, and map sync.

Success criteria:

- Filters support property type, record type, status, verification status, stale flag, city, and state.
- Table rows and map pins stay in sync.
- Selected map pin highlights a table row.
- Selected table row can identify the map pin to zoom/highlight.
- Map workspace response schema has a stable v1 snapshot at `tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json`.
- No Google Maps API or production map provider integration exists yet.

Production gate milestone:

- Real map/location use requires tenant policy, provider policy, production auth, and audit logging.

### V6: Internal Falcon UI Preview

Goal: Render the first internal-only Falcon UI slice against synthetic contracts.

Scope:

- Order Detail Firm Intelligence Found card preview.
- Empty, loading, permission denied, stale warning, and evidence unavailable states.
- Passport detail drawer using the v1 snapshot.
- Historical comp justification modal.
- Audit handoff behavior.
- Optional map workspace preview using synthetic response snapshots.

Success criteria:

- UI renders against versioned synthetic fixtures.
- Client-visible surfaces do not show internal intelligence.
- Permission denied states hide sensitive IDs, counts, and evidence metadata.
- No real evidence opening or source preview exists.

Production gate milestone:

- UI remains synthetic/local or metadata-only until production gates pass.

### V7: Production Readiness Gate and Pilot Controls

Goal: Prepare for an approved metadata-first or single-report pilot without adding extraction code prematurely.

Scope:

- Production readiness gate.
- Production gate review packet.
- Approval workflow for pilot scope, roles, folders, retention, audit, rollback, and success criteria.
- Red/yellow/green allowed action matrix.
- CI/docs checks proving real-content docs reference required gates.

Success criteria:

- Company owner, legal/confidentiality, USPAP/compliance, tenant isolation, security/access, audit logging, and rollback approvals are documented before real-content work.
- Pilot scope lists allowed folders, excluded folders, file types, authorized users, and rollback triggers.
- Metadata-only vs content extraction distinction is explicit.
- Blocked actions remain visible and enforceable.

Production gate milestone:

- Metadata-only real-data scans may proceed only within approved scope.
- Content extraction, OCR, embeddings, and source preview remain blocked until all applicable criteria pass.

### V8: Controlled Real-Data Metadata Pilot

Goal: Validate Falcon Intelligence against approved real metadata without reading content.

Scope:

- One approved tenant.
- One approved folder or assignment set.
- Metadata-only scanning and assignment profiles.
- Tenant-scoped manifests outside the repository.
- Audit events for folder selection, scan start, scan finish, and skipped files.
- Permission checks for internal users.

Success criteria:

- No source content is read, copied, parsed, OCRed, embedded, previewed, or committed.
- Tenant isolation and permission-denied flows pass.
- Metadata outputs are reviewed for leakage.
- Rollback plan is tested.
- Synthetic fallback remains available.

Production gate milestone:

- Metadata-only pilot can complete without opening the content gate.
- Content pilot requires renewed approval.

### V9: Controlled Extraction and Human Verification Pilot

Goal: Test the smallest approved content workflow with human verification.

Scope:

- One approved assignment first.
- One approved report first.
- Approved extraction targets only, starting with low-risk assignment/report metadata.
- Suggested fields only.
- Appraiser/reviewer verification.
- Data passports and evidence links with approved provenance.
- Audit persistence.

Success criteria:

- Suggested values cannot become searchable without human approval.
- Extracted fields have source, method, confidence, verifier, reviewer, and audit references.
- Rejected fields are retained for audit but excluded from normal search.
- No automatic report conclusions or comp selection occur.
- Rollback removes unauthorized derived artifacts according to policy.

Production gate milestone:

- Requires completed production readiness gate and approval packet.
- OCR, embeddings, and source preview each require explicit approval if in scope.

### V10: Premium Knowledge Module at Scale

Goal: Deliver Falcon Intelligence as a premium module integrated with Falcon Core.

Scope:

- Tenant-scoped verified intelligence database.
- Report Intelligence Library.
- Controlled Comp Vault.
- Market Intelligence.
- Property Intelligence.
- Reviewer Assistant.
- Quality Assurance.
- Template Builder and Narrative Engine only after verified structured inputs and narrative controls exist.
- Optional map workspace with approved provider integration.
- Subscription, entitlement, observability, and tenant administration.

Success criteria:

- Falcon Core remains the operational platform.
- Falcon Intelligence is clearly packaged, enabled, billed, and permissioned as a premium knowledge module.
- Tenant isolation, production auth, audit persistence, retention, and rollback are implemented.
- Verified intelligence improves appraiser/reviewer workflow without automating professional conclusions.
- Clients see only explicitly shared deliverables through Falcon Core.
- No cross-firm learning or shared comp vault exists without separate explicit policy.

Production gate milestone:

- Real content, OCR, embeddings, source preview, and narrative workflows are enabled only per tenant, per approved policy, and per feature flag.

## Integration Points With Project Falcon

Falcon Core remains responsible for:

- Orders.
- Assignment workspace.
- User and role management.
- Tenant/company membership.
- Client-facing portals and deliverables.
- Operational status, due dates, and appraiser/reviewer workflow.
- Billing and product entitlements.

Falcon Intelligence integrates through:

- New Order intake: show internal preview when enough seed data exists.
- Order Detail: show Firm Intelligence Found card.
- Assignment workspace: show relevant verified knowledge while work is performed.
- Passport detail drawer: explain provenance for selected matches.
- Evidence-open contract: return safe metadata-only evidence summaries until preview is approved.
- Historical comp justification modal: capture rationale before reuse.
- Intelligence Map Workspace: explore filtered orders, assignments, comps, and intelligence spatially after UI approval.
- Falcon Intelligence Workspace / Map Experience: canonical UX specification for the Map workspace, synchronized table, passport drawer, evidence drawer, and audit drawer.
- Intelligence Workspace State Model: canonical empty, loading, denied, stale, no-results, evidence unavailable, audit unavailable, pending, and error state behavior for Map workspace UI.
- Falcon Shell Integration / Design System Extension: UX commandments, component extension boundaries, visual hierarchy, and Context Bar concept for the Intelligence workspace.
- React Readiness & Contract Gap Review: confirmation that existing v1 synthetic contracts are sufficient for the first internal React workspace preview with no required schema changes.
- Vertical Slice #1: Synchronized Workspace: minimal React preview proving marker/table/summary selection synchronization against existing v1 synthetic map workspace data.
- Audit handoff: Falcon persists viewed, opened, selected, rejected, and justification events in production.
- Permission handoff: Falcon production auth wraps or replaces local policy scaffolds.

## Production Gate Milestones

| Gate | Required before | Key artifacts |
| --- | --- | --- |
| Synthetic contract gate | Any Falcon UI work | Synthetic fixtures, smoke scripts, snapshots, schema registry. |
| Metadata pilot gate | Any real metadata scan | Approved folder scope, tenant/user context, metadata-only policy, rollback plan. |
| Content pilot gate | Any report content extraction or preview | `docs/real-data-production-readiness-gate.md` and `docs/production-gate-review-packet-template.md`. |
| Evidence viewer gate | Any source-document preview | Permission checks, viewer policy, audit persistence, redaction/preview rules. |
| Extraction gate | Any real field extraction | Queue, provenance, human verification, retention, audit, rollback. |
| OCR gate | Any scanned/image text processing | OCR-specific approval, retention, confidence, and review policy. |
| Embedding gate | Any vector representation of content | Tenant-scoped storage, retention, no model training, approval, deletion policy. |
| Narrative gate | Any generated report language | Verified structured inputs, appraiser review, source citation, template policy. |

Blocked until explicitly approved:

- Bulk content extraction.
- Model training on report/client data.
- Cross-firm data mixing.
- Client-visible internal intelligence.
- Uncontrolled evidence preview.
- Repository commits containing real source files or derived content.

## Long-Term Business Vision

Falcon Intelligence should become the premium knowledge layer that makes Project Falcon more valuable over time.

Business outcomes:

- Higher appraiser leverage by surfacing verified prior work at the right time.
- Better reviewer consistency through traceable facts, stale warnings, and audit history.
- Safer comp reuse through data passports, historical justification, and review controls.
- Stronger tenant retention because each firm's verified knowledge base compounds inside Falcon.
- Premium monetization through advanced firm intelligence, QA, comp vault, market memory, map workspace, and future approved narrative workflows.
- Differentiation from generic AI tools through local-first controls, tenant isolation, provenance, and appraisal-specific guardrails.

The long-term product should be powerful because it is trustworthy, not because it is opaque or automatic.

## Roadmap Maintenance Rules

- This document is the canonical planning source for Falcon Intelligence.
- Update this document whenever a roadmap phase changes, a production gate changes, a new premium module is introduced, or Falcon integration scope changes.
- Keep `docs/session-handoff-roadmap.md` as the current implementation checkpoint; keep this document as the long-range product roadmap.
- Do not mark a version complete until success criteria and validation are satisfied.
- Do not add real content work to any version unless the production gate milestone is explicitly satisfied.
- Record new schema surfaces in `docs/schema-version-registry.md` and add snapshots when frontend/API consumers depend on exact shape.
- Keep new implementation slices synthetic/local by default.
- Preserve the statement that Falcon Core is the operational platform and Falcon Intelligence is the premium knowledge module.
- Review this roadmap before planning any major feature slice.
- If this roadmap conflicts with `AGENT_GUIDE.md`, `AGENT_GUIDE.md` wins for repository safety.
