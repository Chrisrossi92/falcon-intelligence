# Falcon Intelligence Architecture

Falcon Intelligence is planned as a future premium Project Falcon module for appraisal firm knowledge work. The first implementation remains a local-first prototype with no real report-content ingestion, no OCR, no embeddings, no vector search, and no cloud sync.

This document defines the intended product architecture before any ingestion or data-processing code is added.

## Architecture Principles

- Local-first by default: private appraisal material stays under the firm's control.
- Firm isolation first: every firm is treated as a separate tenant boundary.
- Metadata before content: the MVP starts with safe folder scanning and metadata indexing only.
- Explicit user control: users choose folders and review what is indexed before any future expansion.
- Premium as an extension: advanced Falcon capabilities live behind feature flags and stable interfaces.
- No cross-firm learning in the pilot: one firm's data must not train, enrich, or search another firm's workspace.

## Product Modules

### Report Intelligence Library

The Report Intelligence Library is the central catalog for appraisal work products once ingestion is approved.

Planned responsibilities:

- Organize report records by client, property, assignment type, effective date, appraiser, reviewer, and status.
- Track document-level metadata without exposing report body text in the MVP.
- Support future retrieval across approved, tenant-owned report content.
- Preserve provenance for every indexed item, including source path, owner, scan time, and indexing status.

MVP boundary:

- Store metadata only.
- Do not read, extract, summarize, or embed report contents.

### Controlled Comp Vault

The Controlled Comp Vault is the governed repository for comparable-sale and lease references.

Planned responsibilities:

- Maintain structured comp records approved by the firm.
- Separate firm-curated comps from public or third-party market inputs.
- Track source confidence, reviewer approval, and usage history.
- Support future controlled reuse across assignments.

MVP boundary:

- Define schema and permissions only.
- Do not import real comp sheets, report tables, or workfile exports.

### Market Intelligence

Market Intelligence is the future module for market observations, trends, and supporting evidence.

Planned responsibilities:

- Organize market notes, datasets, and approved external references.
- Connect market context to property type, geography, date range, and valuation premise.
- Support future trend summaries after approved data pipelines exist.
- Maintain clear separation between firm-owned observations and public market data.

MVP boundary:

- Document planned data categories and ownership rules.
- Do not fetch, scrape, or sync market data.

### Property Intelligence

Property Intelligence is the future property-centric knowledge graph for assignments and assets.

Planned responsibilities:

- Represent properties, parcels, addresses, ownership references, markets, and assignment history.
- Connect properties to reports, comps, inspections, and reviewer notes.
- Support property timelines and relationship mapping.
- Keep tenant-specific property history isolated from other firms.

MVP boundary:

- Define conceptual entities only.
- Do not parse property details from reports or local folders.

### Template Builder

Template Builder is the future workspace for firm-approved report shells, clauses, and reusable structures.

Planned responsibilities:

- Manage approved templates by assignment type, client requirement, property type, and jurisdiction.
- Version template changes with approval history.
- Separate global Falcon templates from firm-specific templates.
- Prepare controlled inputs for the Narrative Engine.

MVP boundary:

- Document template lifecycle and approval states.
- Do not ingest existing Word templates or report shells.

### Narrative Engine

The Narrative Engine is the future drafting assistant for approved report language.

Planned responsibilities:

- Generate draft narrative from approved structured inputs and firm-approved templates.
- Cite source fields and approved references for generated text.
- Preserve reviewer traceability for every generated section.
- Keep human review mandatory before any report use.

MVP boundary:

- Define constraints and review expectations only.
- Do not generate appraisal report language from real report content.

### Reviewer Assistant

Reviewer Assistant is the future workflow module for review comments, consistency checks, and reviewer queues.

Planned responsibilities:

- Route assignments to reviewers based on role, expertise, and workload.
- Track reviewer findings, required changes, and sign-off status.
- Compare submitted metadata against firm requirements.
- Support future content review after ingestion is explicitly approved.

MVP boundary:

- Model roles, statuses, and review events.
- Do not inspect report contents.

### Quality Assurance

Quality Assurance is the future rules and controls layer across Falcon Intelligence.

Planned responsibilities:

- Run policy checks, completeness checks, and consistency checks.
- Maintain auditable QA results by tenant, assignment, module, and reviewer.
- Flag missing metadata, stale sources, or permission issues.
- Enforce data-handling guardrails before content pipelines run.

MVP boundary:

- Start with safety checks around file selection, ignored file types, and metadata-only indexing.
- Do not run report-content QA.

## Data Ownership Model

Falcon Intelligence treats each appraisal firm as the owner of its own workspace data.

Ownership rules:

- The firm owns its reports, workfiles, comp records, templates, reviewer notes, and metadata.
- Falcon provides software boundaries, module interfaces, and optional future managed infrastructure.
- Users own only the records they create within the permissions granted by their firm.
- Clients may receive limited, assignment-specific access when the firm explicitly grants it.
- Premium Falcon-wide product metadata must remain separate from firm-owned assignment data.

Data classes:

- Firm-owned private data: reports, workfiles, comps, templates, notes, QA findings, and metadata.
- User activity data: audit events, review actions, approvals, and configuration changes.
- Falcon product data: feature flags, module definitions, billing state, and system configuration.
- Public or licensed reference data: future external market inputs governed by their own license terms.

No real firm-owned private data should be committed to this repository.

## Tenant Isolation Model

Every firm is modeled as a tenant. Tenant isolation is required at storage, authorization, indexing, logging, and future retrieval layers.

Required isolation boundaries:

- Tenant identifier on every firm-owned record.
- Separate authorization checks for every tenant-scoped action.
- Tenant-scoped indexes when indexing is eventually approved.
- Tenant-scoped audit logs and admin controls.
- No shared vector store across firms in the pilot.
- No background process that reads one tenant's files while operating in another tenant context.

Future managed architecture should enforce tenant isolation through database row-level security, storage path policies, service-role boundaries, and module-level permission checks.

## Continental-First Pilot Model

The first pilot is Continental-first: one firm, one controlled tenant, and no cross-firm data mixing.

Pilot assumptions:

- Continental operates as the initial tenant.
- All local prototype data remains on Continental-controlled machines or approved local storage.
- The pilot does not combine Continental data with another firm's data.
- The pilot does not use Continental data to seed a shared Falcon knowledge base.
- Future demo data must be synthetic unless Continental explicitly approves a separate sanitized dataset.

Pilot success should be measured by safe indexing flow, metadata quality, permission fit, and reviewer workflow clarity before any content ingestion is considered.

## Permission Model

Permissions should be role-based with tenant-level enforcement and assignment-level overrides where needed.

| Role | Intended Access |
| --- | --- |
| Owner | Full tenant control, billing, module enablement, data retention policy, user management, and audit access. |
| Admin | Operational configuration, user management, folder selection, metadata index management, template administration, and QA policy configuration. |
| Appraiser | Access to assigned matters, approved templates, firm comps, metadata search, and draft workflows allowed by policy. |
| Reviewer | Access to assigned review queues, report metadata, QA findings, review comments, and sign-off workflows. |
| Trainee | Limited access to assigned matters, training templates, and reviewer-supervised workflows. No tenant-wide export or admin settings. |
| Client | Narrow assignment-specific access granted by the firm. No firm library search, comp vault access, or internal reviewer notes unless explicitly shared. |

Baseline permission rules:

- Default deny for new modules and sensitive actions.
- Owners and admins manage users, but only owners manage tenant-level commercial controls.
- Appraisers and trainees cannot change tenant safety settings.
- Reviewers can approve or reject workflow items but cannot override tenant data policies.
- Client access is external-facing, revocable, and scoped to specific deliverables.

## Local-First Prototype Architecture

The local-first prototype should run with minimal assumptions and no external data services.

Prototype layers:

- User-selected folders: future inputs selected through explicit local UI controls.
- Safety gate: validates path scope, ignored file types, and metadata-only mode.
- Metadata scanner: future component that records file name, extension, size, timestamps, and stable local identifiers.
- Local metadata store: future local database for non-content metadata only.
- Module services: framework services for library, review, QA, and premium extension boundaries.
- Local UI: future interface for reviewing scan results and module state.

Prototype restrictions:

- No report body extraction.
- No OCR.
- No embeddings.
- No vector database.
- No summarization.
- No cloud sync.
- No automatic folder crawling outside approved paths.
- No OneDrive report-folder access during framework development.

## Future Falcon/Supabase Architecture

The future managed Falcon architecture may use Supabase for tenant-aware application storage, authentication, authorization, and operational services.

Candidate managed layers:

- Supabase Auth for users, roles, invitations, and client access.
- Postgres tables with tenant identifiers and row-level security.
- Supabase Storage for approved tenant files if cloud storage is explicitly enabled.
- Edge functions or service workers for controlled background workflows.
- Tenant-scoped indexing services after ingestion approval.
- Audit tables for permission changes, scans, reviews, QA events, and exports.

Future architecture constraints:

- Row-level security must be mandatory for tenant-scoped tables.
- Service-role operations must be narrow, logged, and reviewed.
- Storage buckets must separate tenant content from Falcon product assets.
- Any future embeddings must be tenant-scoped and non-shared by default.
- Cross-tenant analytics must use aggregate, non-identifying product metrics only.

## MVP Roadmap

### Phase 0: Documentation and Safety Scaffold

Current phase.

- Define product architecture and safety boundaries.
- Maintain `.gitignore` protections for document and data formats.
- Keep premium module disabled.
- Keep ingestion code out of scope.

### Phase 1: Safe Folder Scanning

First implementation phase after approval.

- Add explicit folder selection.
- Validate selected paths against configured safety rules.
- Record metadata only: file name, extension, size, modified time, and scan status.
- Skip blocked file types by default unless policy allows metadata-only visibility.
- Show users what would be indexed before storing metadata.

No report contents are read in this phase.

See `docs/metadata-scanning.md` for the current metadata-only scanner boundary.

### Phase 2: Metadata Indexing

- Store local metadata in a local database.
- Add tenant and user context to every metadata record.
- Add audit events for folder selection, scan start, scan finish, and skipped files.
- Add filters for assignment year, file type, folder, and scan status.

No report contents are read in this phase.

### Phase 3: Review and QA Workflow Shell

- Add review queues, status transitions, and QA policy placeholders.
- Link metadata records to assignments without parsing document bodies.
- Add role-based access checks.
- Add synthetic fixtures for tests.

### Phase 4: Controlled Content Evaluation

Only after explicit approval.

- Define approved synthetic or sanitized corpus.
- Add content extraction experiments outside real report folders.
- Evaluate redaction, logging, review, and retention rules.
- Require sign-off before any real report-content pipeline exists.

## Current Guardrail

No real report contents are ingested yet.

The current repository must remain limited to source code, documentation, safety checks, and synthetic tests. Future ingestion, extraction, OCR, embeddings, vector search, summarization, and report drafting must remain disabled until explicitly approved and documented.
