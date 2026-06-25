# Session Handoff and Roadmap Checkpoint

This checkpoint summarizes the current Falcon Intelligence prototype state and recommended next direction. It does not authorize real data access, OneDrive access, report parsing, extraction, OCR, embeddings, or ingestion.

For canonical long-range product planning, see `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md`. This handoff remains the current implementation checkpoint.

## Product Vision

Falcon Intelligence is a local-first appraisal firm knowledge base prototype. The near-term product direction is an internal-only "Firm Intelligence Found" experience that helps Project Falcon surface prior verified firm knowledge while an order is being created, reviewed, or worked.

The product should help appraisers and reviewers answer:

- Have we seen this subject property before?
- Do we have relevant prior assignments, sale comps, lease comps, or market indicators?
- Why should a surfaced fact be trusted?
- Where is the provenance, evidence, and audit trail?

Falcon Intelligence is assistive. It must not produce automatic valuation conclusions or automatic report language without appraiser review.

## Safety and Data Boundaries

Current non-negotiable boundaries:

- Use committed synthetic fixtures only.
- Do not add real appraisal reports, client files, source documents, OneDrive exports, extracted text, OCR output, embeddings, vector stores, databases, PDFs, DOCX, XLSX, CSV, TSV, or TXT exports.
- Do not read report contents.
- Do not inspect unrelated OneDrive files.
- Do not add extraction, OCR, embedding, retrieval, or report parsing code.
- Keep all current workflows metadata-only and local.

Explicit warning: do not add real report extraction yet. Metadata-only real-data scans are allowed, but report content extraction, OCR, embeddings, and source-document preview are blocked until `docs/real-data-production-readiness-gate.md` passes.

## Implemented So Far

Core scaffold:

- Local-first package scaffold in `src/falcon_intel`.
- Safety and architecture documentation under `docs/`.
- Development setup with `pytest` as a dev dependency.
- GitHub Actions validation workflow.

Synthetic metadata workflows:

- Metadata scanner, manifest creation, manifest search, assignment discovery, and assignment profile generation.
- Committed synthetic sample fixture tree under `tests/fixtures/synthetic_sample_data/`.
- Synthetic manifests and assignment profiles for industrial, retail, office, purchase, lease-heavy, and work-in-progress assignments.

Firm Intelligence card prototype:

- Synthetic verified intelligence fixture at `tests/fixtures/synthetic_verified_intelligence/verified-intelligence.json`.
- Synthetic matcher for fake Falcon order payloads.
- CLI preview command for the Firm Intelligence Found card.
- Stable UI-facing v1 card schema with snapshot fixture at `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json`.
- Local Falcon-style card contract boundary for synthetic card responses.

Trust, provenance, and audit scaffolding:

- Stable policy codes for match categories, warning codes, action codes, and audit events.
- Local audit event builders for card view, evidence open, match select/reject, and justification.
- Historical comparable justification model and reusable narrative draft.
- Evidence link model for future "open evidence" behavior.
- Data passport model for full provenance detail.
- Compact passport summaries on top match cards.
- Synthetic data passport detail fixture at `tests/fixtures/synthetic_data_passports/data-passports.json`.
- Local passport detail lookup from `tenant_id` and `passport_id`.
- Falcon-style passport detail contract boundary with suggested `opened_evidence` audit event.
- Versioned synthetic passport detail drawer UI contract snapshot at `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json`.
- Falcon-style evidence-open contract boundary that validates an evidence link belongs to a passport and returns a metadata-only summary plus suggested audit event.
- Synthetic/local permission policy scaffold for internal role and evidence visibility decisions.
- End-to-end synthetic workflow that builds a card, opens passport detail, checks permissions, opens evidence, and returns suggested audit payloads.
- Documentation-only real data production readiness gate at `docs/real-data-production-readiness-gate.md`.
- Documentation-only production gate review packet template at `docs/production-gate-review-packet-template.md`.
- Documentation-only Falcon UI integration notes at `docs/falcon-ui-integration-notes.md`.
- Synthetic/local Intelligence Map Workspace contract at `docs/intelligence-map-workspace-contract.md`.
- Versioned synthetic Map Workspace UI response snapshot at `tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json`.
- Documentation-only Falcon Intelligence Workspace / Map Experience specification at `docs/intelligence-workspace-map-experience.md`.
- Documentation-only Intelligence Workspace State Model at `docs/intelligence-workspace-state-model.md`.
- Documentation-only Falcon Shell Integration / Design System Extension at `docs/intelligence-workspace-falcon-shell-integration.md`.
- Documentation-only React Readiness & Contract Gap Review at `docs/react-readiness-contract-gap-review.md`.
- Minimal internal React synchronized Map workspace preview under `frontend/`.
- Minimal internal React Passport drawer preview in the workspace, using existing synthetic passport snapshots/contracts and preserving map/table context.
- Minimal internal React Evidence drawer preview in the workspace, using the existing metadata-only Evidence Link Model and Evidence Open Contract while preserving Passport and map/table context.
- Minimal internal React Audit Timeline drawer preview in the workspace, using existing synthetic audit event snapshots/contracts while preserving Evidence, Passport, and map/table context.
- Minimal internal React Workspace State Rendering preview with preview-only simulated loading, empty, permission denied, stale, no-results, evidence unavailable, audit unavailable, and error states.
- Minimal internal React Context Bar preview with derived workspace, selected property, Passport, Evidence, Audit, and state-context language.
- Canonical master product roadmap at `FALCON_INTELLIGENCE_PRODUCT_ROADMAP.md`.
- Lightweight schema version registry at `docs/schema-version-registry.md` and `src/falcon_intel/schema_registry.py`.
- Versioned synthetic Falcon API envelope snapshots at `tests/fixtures/synthetic_api_envelopes/`.
- Versioned synthetic audit event snapshots at `tests/fixtures/synthetic_audit_events/`.

## Current Validation Status

Current local validation is passing.

Run full validation:

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
PYTHONPATH=src python3 scripts/smoke_map_workspace.py
PYTHONPATH=src python3 scripts/smoke_map_workspace_snapshot.py
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
cd frontend
npm test
npm run build
```

CI runs the same synthetic-only core checks on push and pull request.

## Synthetic and Local Only

The following remain synthetic/local only:

- Matcher scoring and ranking.
- Verified intelligence records.
- Data passport details.
- Evidence links.
- Audit events.
- Falcon card, passport, and evidence-open contract boundaries, including optional synthetic permission checks.
- Historical comparable justification narratives.
- UI card and passport detail drawer snapshots.
- Falcon API envelope snapshots.
- Audit event snapshots.
- Permission decisions.
- Intelligence Map Workspace records, filters, and map/table serializer.
- Intelligence Map Workspace UI response snapshot.
- Falcon Intelligence Workspace UX, state, Falcon shell integration, and React readiness specifications.
- Internal React synchronized workspace preview against the v1 synthetic map workspace snapshot.
- Internal React Passport drawer preview against existing v1 synthetic passport snapshots/contracts.
- Internal React Evidence drawer preview against the existing metadata-only evidence-open contract.
- Internal React Audit Timeline drawer preview against existing synthetic audit event snapshots/contracts.
- Internal React Workspace State Rendering preview using derived local UI state only.
- Internal React Context Bar preview using derived local UI state and existing synthetic contracts only.
- Internal React Layer Panel preview using derived local UI state and existing synthetic map/passport/evidence/audit metadata only.
- Internal React Accessibility and Keyboard Navigation pass for markers, table rows, layer controls, Context Bar semantics, and nested drawer focus/Escape behavior.
- Internal React Visual Polish and Falcon Shell Alignment pass for spacing, density, map/table/drawer hierarchy, and restrained platform styling.
- Documentation-only internal V2 design review at `docs/internal-design-review-v2.md`.
- Internal React Knowledge Summary Trust Panel that reframes the selected property summary with derived property identity, trust status, verified fact, evidence, audit activity, review metadata, and next-step Passport guidance.
- Internal React First-Time Workflow Guidance with local dismissible Map-to-Property-to-Knowledge-Summary-to-Passport-to-Evidence-to-Audit guidance and subtle Passport/Evidence drawer hints.
- Internal React Passport Information Architecture pass that reorganizes Passport into Identity, Verified Knowledge, Evidence, Verification / Review, and Related Work while preserving all nested drawer interactions.
- Internal React Evidence Readability pass that reorganizes Evidence into Evidence Summary, Source Metadata, Trust Context, and Audit Handoff while preserving metadata-only limitations and Audit handoff behavior.
- Internal React Audit Timeline pass that presents existing synthetic audit events as a readable Timeline Summary, Chronological Timeline, and Current Status without adding production audit services.
- Documentation-only V3 Workflow Comprehension Review at `docs/workflow-comprehension-review-v3.md`.
- Documentation-only V3 Guided Stakeholder Review Packet at `docs/stakeholder-review-packet-v3.md`.
- Internal synthetic dataset expansion for the Map workspace, including the airport warehouse demo scenario, unverified retail lead, multiple property types/statuses, evidence/no-evidence records, and audit/no-audit behavior using existing v1 contract shapes.
- Internal React Realistic Filter/Search Preview with local search and filters for property type, verification status, evidence availability, audit activity, and record status while keeping Layer Panel behavior separate.
- Documentation-only V3 Demo Readiness Review at `docs/demo-readiness-review-v3.md`, concluding the airport warehouse scenario is ready for a guided internal demo with clear synthetic-preview framing.
- Internal React V3.5A Spatial Continuity Pass that tightens drawer anchoring, selected marker/row persistence, Knowledge Summary anchoring, and visual continuity while Passport, Evidence, and Audit drawers are open.
- Internal React V3.5B Visual Rhythm Pass that refines spacing cadence, typography hierarchy, divider consistency, filter/layer/table rhythm, Knowledge Summary density, and Passport/Evidence/Audit drawer spacing without adding features.
- Internal React V3.5C Language Audit that refines visible UI copy toward appraiser-natural language, supporting evidence, review history, calm preview limitations, and defensible trust terminology without adding features.
- Internal React V3.5D Interaction Consistency Pass that aligns repeated selection, drawer, button, filter, layer, status, close-control, hover, disabled, and terminology patterns without adding features.
- Documentation-only V3.5E Workspace Cohesion Review at `docs/workspace-cohesion-review-v3_5.md`, concluding the workspace foundation is internally coherent and ready for guided stakeholder review and V4 planning.
- Internal React V3.5F Layout De-Clutter / Mockup Alignment Pass that moves Layers out of the map overlay and into a stable right rail above Knowledge Summary, with Filters, Map, Table, Layers, and Knowledge Summary arranged as clean cards.

None of these are production APIs, database queries, permission checks, source-document viewers, report readers, or extraction systems.

## Project Falcon Tie-In

Falcon Intelligence currently supports Project Falcon integration through local contract helpers:

- `build_falcon_intelligence_card_response`: accepts a Falcon-style synthetic order payload and returns the v1 Firm Intelligence Found card.
- `build_falcon_passport_detail_response`: accepts `tenant_id`, `order_id`, `user_id`, and `passport_id`, then returns full synthetic passport detail plus a suggested audit event.

Future Falcon UI placement:

- Order Detail.
- New Order intake.
- Assignment workspace.
- Intelligence Map workspace.

Visibility must remain internal-only. Client-facing views must not show Firm Intelligence cards, passport details, evidence links, audit metadata, reviewer notes, or internal comp/fact recommendations.

## Recommended Next 5 Slices

1. Run the guided stakeholder review with at least one appraiser, one reviewer, and one owner/admin using the airport warehouse scenario.
2. Synthesize stakeholder findings into a V3.5 review outcome memo with go/no-go recommendation for V4 planning.
3. Begin V4 planning around permission/trust hardening, production-readiness boundaries, and demo-safe fixture polish.
4. Decide whether the preview-only state simulator should move out of the production-like workspace frame before stakeholder demos.
5. Permission role matrix review: decide whether owner/admin should continue to inherit `appraiser_reviewer_only` evidence access in production.

## Current Known Risks

- Current matching is deterministic synthetic scoring, not production relevance logic.
- No production tenant isolation, auth, or permission enforcement exists.
- Permission policy is a local scaffold only and is not production auth.
- Permission-aware contract behavior is optional and synthetic; production Falcon must enforce real auth and order access separately.
- Suggested audit events are not persisted.
- Evidence links are placeholders and do not open source documents.
- Data passport fixtures cover only selected synthetic records.
- Passport drawer preview is metadata-only and relies on nested Evidence/Audit drawers for deeper provenance.
- Evidence drawer preview is metadata-only and intentionally does not include source previews.
- Audit Timeline drawer preview is fixture-backed metadata only and is not production audit history.
- Workspace state rendering is preview-only local simulation and is not a production state service or permission backend.
- Context Bar preview is derived presentation text only and is not a new contract or breadcrumb/navigation system.
- Layer Panel preview is derived local UI state only and is not a production GIS layer model, backend filter service, search feature, or map provider integration.
- Accessibility and keyboard behavior is a preview pass only; it is not a complete production accessibility audit.
- Visual polish is CSS/local UI composition only and is not production Falcon design-system integration.
- Knowledge Summary indicators are locally derived from existing synthetic passport, evidence, and audit metadata; they are not production trust scores, production reviewer approvals, or production source-access guarantees.
- First-Time Workflow Guidance is local preview state only; it is not persisted onboarding, telemetry, or a production training system.
- Passport Information Architecture is local UI grouping over existing synthetic contracts; it does not add fields, source access, backend behavior, or production verification claims.
- Evidence Readability is local UI grouping over existing metadata-only evidence contracts; it does not add source preview, extraction, OCR, or real file access.
- Audit Timeline presentation is local UI grouping over existing synthetic audit event snapshots; it is not production audit persistence, reviewer approval, or production audit history.
- V3 Workflow Comprehension Review concludes the UX blueprint is coherent, but stakeholder-demo readiness still requires guided narration and production UX readiness is not achieved.
- V3 Stakeholder Review Packet is documentation-only and does not authorize real data, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, production map provider, or backend work.
- V3 Synthetic Dataset Expansion improves demo realism with local fixtures only; it does not introduce real reports, client data, new schemas, backend behavior, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or production map provider work.
- V3 Realistic Filter/Search Preview is local UI filtering over synthetic records only; it is not production search, backend filtering, embeddings, or a search service.
- V3 Demo Readiness Review supports a guided internal demo only; it does not mean the preview is ready for unguided stakeholder testing, production pilots, real data demonstrations, source preview, or production search.
- V3.5A Spatial Continuity Pass is styling and layout-state only; it does not add features, schemas, backend behavior, production map provider work, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or real data.
- V3.5B Visual Rhythm Pass is CSS-only refinement; it does not add interactions, data, schemas, backend behavior, production map provider work, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or real data.
- V3.5C Language Audit is visible-copy refinement only; it does not add interactions, data, schemas, backend behavior, production map provider work, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or real data.
- V3.5D Interaction Consistency Pass is local UI interaction, copy, accessible-label, and CSS feedback refinement only; it does not add features, schemas, backend behavior, data changes, production map provider work, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or real data.
- V3.5E Workspace Cohesion Review is documentation-only; it does not authorize UI changes, code changes, features, schemas, backend behavior, production architecture, production map provider work, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or real data.
- V3.5F Layout De-Clutter / Mockup Alignment Pass is local markup/CSS layout refinement only; it does not add features, schemas, backend behavior, data changes, production map provider work, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or real data.
- UI schemas are stable enough for prototype work but may need versioning as frontend requirements mature.
- React readiness review concludes the first workspace preview can begin without required schema changes, but implementation may still reveal optional UI convenience fields later.
- The first React workspace preview proves synchronization only; it does not include passport, evidence, audit drawers, real map provider behavior, search, clustering, advanced filters, production styling, or production data.
- Schema versions and API envelope snapshots are registered, but these still describe local synthetic contracts rather than production APIs.
- The repository contains no approved ingestion or extraction pipeline; adding one prematurely would violate the current safety boundary.
- Real content work remains blocked until the production readiness gate passes; metadata-only scans are the only allowed real-data activity.
- CI validates synthetic workflows only and cannot prove production readiness.
