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
