# Falcon Order Intelligence Loop

This document designs how future Falcon orders connect to Falcon Intelligence assignments, reports, verified facts, and recommendations. It is documentation-only and does not authorize extraction code, report reading, OCR, embeddings, copying files, or ingestion of real appraisal reports.

The goal is to make each order a structured seed record that can later benefit from verified firm intelligence while preserving appraiser judgment, tenant isolation, provenance, and auditability.

## Order as Seed Record

A Falcon order should become the first structured context record for a future assignment.

Seed fields:

- Client.
- Borrower/contact.
- Address.
- Property type.
- Intended use.
- Appraiser.
- Reviewer.
- Due dates.
- Engagement/source documents.

Order records should also capture:

- Tenant ID.
- Order status.
- Ordering party.
- Internal job number.
- Scope notes.
- Required report type.
- Delivery requirements.
- Source document metadata.
- Permission context.

The seed record should not be treated as verified intelligence. It provides initial context for assignment matching, routing, and future review.

## Assignment Lifecycle

The order-to-intelligence lifecycle should move through controlled states:

1. Order created.
2. Source documents uploaded.
3. Report in progress.
4. Report completed.
5. Assignment profile created.
6. Verified intelligence extracted.
7. Intelligence promoted to firm knowledge base.

### Order Created

The order is entered with client, borrower/contact, property, scope, appraiser, reviewer, due date, and engagement metadata.

### Source Documents Uploaded

The firm adds engagement letters, prior reports, rent rolls, plans, leases, surveys, or other source materials under approved storage policy. Source-document metadata can be tracked before any content is read.

### Report in Progress

The appraiser works the assignment. Falcon may show metadata-only or verified-intelligence recommendations, but the appraiser remains responsible for deciding relevance and use.

### Report Completed

The report artifact is marked complete. This can make the assignment eligible for metadata scanning, assignment profiling, and future human-approved extraction.

### Assignment Profile Created

Falcon creates a metadata-only assignment profile from the completed assignment's manifest and discovered folder. This profile becomes the bridge to future extraction review.

### Verified Intelligence Extracted

After explicit approval, future extraction may propose suggested fields. Appraisers and reviewers verify, edit, reject, or archive those suggestions.

### Intelligence Promoted to Firm Knowledge Base

Verified fields become searchable only when tenant policy, provenance, permissions, stale-data policy, and reviewer approval requirements are satisfied.

## Matching Logic for New Orders

When a new order is created, Falcon can search verified firm intelligence for possible matches. Matching should produce recommendations, not conclusions.

Matching signals:

- Same subject property.
- Nearby properties.
- Same borrower/client.
- Same property type.
- Similar building size.
- Similar market.
- Prior sale/lease comps.

Matching should rank candidates by:

- Exact address or parcel match.
- Distance and market/submarket fit.
- Property type and subtype.
- Building size band.
- Date recency and stale policy.
- Verification status.
- Source quality.
- Reviewer approval.
- Historical consistency.

No recommendation should be used automatically. Each surfaced item should include provenance and require appraiser judgment before use.

## Firm Intelligence Found Card

The future order workspace should show a "Firm Intelligence Found" card when verified tenant-scoped intelligence may be relevant.

Card sections:

- Nearby prior assignments.
- Prior subject matches.
- Verified sale comps.
- Verified lease comps.
- Relevant market indicators.
- Relevant report sections.
- Confidence/provenance display.

Each item should show:

- Match reason.
- Confidence dimensions.
- Data passport summary.
- Freshness or stale warning.
- Source assignment/report reference.
- Verification and reviewer status.
- Permission-limited evidence links.

The card should never expose internal intelligence to clients unless the firm explicitly shares a deliverable.

## Feedback Loop

Completed orders should improve future recommendations only after verification.

Feedback rules:

- Completed orders can feed future recommendations through verified intelligence records.
- Verified facts remain linked to the order, assignment, report artifact, source documents, verification record, and audit events.
- Rejected facts do not become searchable.
- Historical data is shown with stale-data warnings.
- New verified intelligence should not overwrite older records without versioning.
- Reuse of historical comparables should create a new audit event and appraiser justification.

The feedback loop should strengthen the firm's internal knowledge base without creating automatic reliance on prior conclusions.

## Permission Model

Visibility and actions should be role-scoped.

| Role | Order Intelligence Visibility |
| --- | --- |
| Owner | Tenant-wide visibility into orders, verified intelligence, dashboard health, audit events, and policy settings. |
| Admin | Operational visibility into orders, source metadata, assignment status, queues, and policy-managed intelligence surfaces. |
| Appraiser | Access to assigned orders, relevant verified firm intelligence, data passports, evidence links permitted by role, and audit-tracked reuse actions. |
| Reviewer | Access to review queues, relevant order context, verification records, reviewer notes, stale warnings, and QA-relevant evidence. |
| Client | Access only to explicitly shared order status or deliverables. No internal firm intelligence, comp vault, reviewer notes, source evidence links, or data passports by default. |

Permission rules:

- Clients cannot see internal intelligence.
- Appraisers can use intelligence with an audit trail.
- Reviewers can approve or reject surfaced intelligence according to firm policy.
- Admins can configure matching and visibility rules but should not bypass valuation-fact approval.
- Owners can set tenant-level policy and review audit history.

## Future Falcon/Supabase Mapping

Candidate tables:

- `orders`
- `assignments`
- `report_artifacts`
- `verified_subject_facts`
- `verified_sale_comps`
- `verified_lease_comps`
- `market_indicators`
- `intelligence_matches`
- `audit_events`

Supporting tables:

- `source_documents`
- `assignment_profiles`
- `verification_records`
- `data_passports`
- `evidence_links`
- `field_versions`
- `historical_reuse_justifications`

Implementation notes:

- `orders` should seed `assignments` but remain distinct from verified intelligence.
- `intelligence_matches` should store match reason, score, source entity, order ID, and user action.
- `report_artifacts` should track completed report metadata and source linkage.
- Verified fact tables should require `tenant_id`, `assignment_id`, `source_document_id`, and `verification_record_id`.
- `audit_events` should record when surfaced intelligence is viewed, selected, rejected, reused, or overridden.
- Supabase row-level security should enforce tenant isolation across all order and intelligence tables.

## Guardrails

Required guardrails:

- No cross-firm data mixing.
- No automatic reliance on prior comps.
- Appraiser remains responsible.
- All surfaced facts must be traceable.
- Rejected facts do not become searchable.
- Stale or historical data must show warnings.
- Reuse requires appraiser justification when policy requires it.
- Clients cannot see internal firm intelligence.
- Search and recommendation indexes remain tenant-scoped.

The order intelligence loop should assist appraisers by surfacing prior verified knowledge, not by making valuation decisions.

## Current Guardrail

This is a design document only. Falcon Intelligence currently supports metadata-only scanning, local manifests, metadata search, assignment discovery, and assignment profile export. It does not read report contents, extract text, preview reports, OCR documents, create embeddings, copy files, or ingest appraisal reports.
