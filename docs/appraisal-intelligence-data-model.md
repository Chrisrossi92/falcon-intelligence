# Appraisal Intelligence Data Model

This document defines the future verified intelligence database for Falcon Intelligence. It is documentation-only. It does not authorize extraction, report parsing, OCR, embeddings, or ingestion of real report contents.

The model separates suggested intelligence from verified firm-searchable intelligence. Every entity must remain tenant-isolated, appraiser-controlled, and auditable.

## Status Definitions

### Suggested

Suggested records are draft intelligence candidates created by a user, future AI-assisted workflow, or metadata process. Suggested records are not firm-searchable by default, cannot be used as verified comparables, and require appraiser or reviewer action before promotion.

### Verified

Verified records have been reviewed and approved by an authorized appraiser, reviewer, or admin under firm policy. Verified records may become firm-searchable when the entity type allows it and tenant policy permits it.

### Rejected

Rejected records were reviewed and declined. They should remain auditable but should not appear in ordinary search results, comp selection flows, or market intelligence outputs unless an admin explicitly reviews rejected history.

## Entity Model

| Entity | Purpose | Key Fields | Source of Truth | AI-Suggested | Requires Appraiser Approval | Firm-Searchable | Tenant Isolation | Future Falcon/Supabase Mapping |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Assignment | Represents an appraisal engagement or work item. | `assignment_id`, `tenant_id`, `client_id`, `property_id`, `assignment_type`, `effective_date`, `report_date`, `status`, `appraiser_id`, `reviewer_id`, `source_manifest_id` | Firm assignment system or approved user entry. | Yes, from metadata-only folder discovery or future extraction. | Yes, before use in production workflows. | Yes, after verification. | Tenant-scoped; no assignment record crosses firm boundaries. | `assignments` with RLS on `tenant_id`; linked to `properties`, `source_documents`, and `audit_events`. |
| Subject Property | Represents the property being appraised. | `property_id`, `tenant_id`, `assignment_id`, `address`, `parcel_id`, `property_type`, `subtype`, `market`, `submarket`, `coordinates`, `ownership_interest` | Appraiser-approved assignment data. | Yes, after future controlled extraction or user draft entry. | Yes. | Yes, when verified and policy allows property history search. | Tenant-scoped; property history cannot merge across firms. | `subject_properties`; optional shared `property_aliases` per tenant only. |
| Building/Improvement | Describes improvements on the subject or comparable property. | `improvement_id`, `tenant_id`, `property_id`, `building_type`, `year_built`, `renovation_year`, `gla`, `nra`, `units`, `stories`, `condition`, `quality`, `parking`, `amenities` | Appraiser verification, inspection notes, approved source documents. | Yes. | Yes. | Yes, if linked to verified property or comp. | Tenant-scoped; improvement facts stay with tenant-owned records. | `improvements`; foreign key to tenant-scoped `properties` or comparables. |
| Land/Site | Captures site characteristics for subject or comparable properties. | `site_id`, `tenant_id`, `property_id`, `land_area`, `zoning`, `frontage`, `access`, `utilities`, `topography`, `flood_zone`, `environmental_notes`, `entitlements` | Appraiser verification and approved public/source records. | Yes. | Yes. | Yes, when verified. | Tenant-scoped; source attribution required for shared firm search. | `land_sites`; linked to `properties`, `source_documents`, and `verification_records`. |
| Sale Comparable | Verified or candidate sale used as market evidence. | `sale_comp_id`, `tenant_id`, `property_id`, `sale_date`, `sale_price`, `price_per_unit`, `price_per_sf`, `buyer`, `seller`, `conditions_of_sale`, `financing`, `property_rights`, `verification_status`, `stale_after` | Appraiser-approved sale record and verification source. | Yes. | Yes, before comp vault use. | Yes, only when verified and not stale under policy. | Tenant-scoped; no cross-firm comp vault mixing. | `sale_comparables`; RLS by `tenant_id`; linked to `verification_records`. |
| Lease Comparable | Verified or candidate lease used as rent evidence. | `lease_comp_id`, `tenant_id`, `property_id`, `tenant_name`, `lease_date`, `commencement_date`, `term_months`, `rent`, `rent_basis`, `escalations`, `concessions`, `expense_structure`, `verification_status`, `stale_after` | Signed lease, rent roll, broker confirmation, or appraiser-approved source. | Yes. | Yes. | Yes, only when verified and permission allows. | Tenant-scoped; confidential lease terms never cross firms. | `lease_comparables`; linked to `source_documents`, `properties`, and `verification_records`. |
| Listing Comparable | Active or historical listing evidence. | `listing_comp_id`, `tenant_id`, `property_id`, `listing_date`, `asking_price`, `asking_rent`, `broker`, `listing_status`, `days_on_market`, `source_url`, `stale_after` | Approved listing source or appraiser-entered evidence. | Yes. | Yes. | Yes, with freshness warnings. | Tenant-scoped; source license and confidentiality tracked per tenant. | `listing_comparables`; optional `external_sources` link. |
| Expense Comparable | Operating expense evidence from properties or market data. | `expense_comp_id`, `tenant_id`, `property_type`, `market`, `expense_year`, `expense_category`, `amount`, `unit_basis`, `occupancy`, `source_type`, `verification_status`, `stale_after` | Appraiser-approved operating statements, surveys, or firm datasets. | Yes. | Yes. | Yes, when aggregated or permission-approved. | Tenant-scoped; property-specific expense data may require stricter access. | `expense_comparables`; linked to `verification_records` and optional `market_indicators`. |
| Market Indicator | Verified market observation or metric. | `indicator_id`, `tenant_id`, `market`, `submarket`, `property_type`, `indicator_type`, `value`, `unit`, `date_range`, `source_count`, `confidence`, `stale_after` | Verified saved report data, approved datasets, or appraiser research. | Yes. | Yes. | Yes, after verification and freshness checks. | Tenant-scoped; only aggregate non-identifying indicators may support future cross-tenant product analytics. | `market_indicators`; optional aggregate tables with strict de-identification. |
| Report Section | Structured reference to a report section, not extracted text by default. | `section_id`, `tenant_id`, `assignment_id`, `section_type`, `section_label`, `page_range`, `status`, `approved_summary_id`, `source_document_id` | Approved report outline or future controlled extraction. | Yes. | Yes before use in narrative systems. | Limited; section metadata can be searchable, body text only after future approval. | Tenant-scoped; report section content never crosses tenant boundary. | `report_sections`; content fields disabled until ingestion approval. |
| Source Document | Metadata record for a document connected to an assignment or evidence item. | `source_document_id`, `tenant_id`, `assignment_id`, `relative_path`, `file_name`, `extension`, `file_size`, `modified_timestamp`, `manifest_id`, `content_ingested`, `absolute_path_allowed` | Metadata scanner and user approval. | Yes, metadata only. | Yes for linking to verified intelligence. | Metadata can be searchable; contents remain unavailable until approved ingestion. | Tenant-scoped; absolute path handling follows manifest privacy policy. | `source_documents`; storage references tenant-scoped; content fields null by default. |
| Verification Record | Captures review, source, and approval state for intelligence. | `verification_id`, `tenant_id`, `entity_type`, `entity_id`, `status`, `verified_by`, `verified_at`, `source_document_id`, `confidence`, `notes`, `rejection_reason` | Authorized appraiser, reviewer, or admin decision. | No, but AI can suggest fields requiring verification. | Yes, by definition. | Supports firm-searchable promotion. | Tenant-scoped; verification history cannot be shared across firms. | `verification_records`; immutable audit-style rows with RLS. |
| Reviewer Note | Internal review comment or QA note. | `reviewer_note_id`, `tenant_id`, `assignment_id`, `entity_type`, `entity_id`, `author_id`, `note_type`, `body_reference`, `severity`, `status`, `created_at`, `resolved_at` | Reviewer or authorized user. | Yes, future AI may suggest note candidates. | Yes before becoming formal QA finding. | Limited; internal review notes are not client-searchable by default. | Tenant-scoped; client access requires explicit sharing. | `reviewer_notes`; linked to `assignments`, `users`, and `audit_events`. |
| Audit Event | Immutable event record for system and user actions. | `audit_event_id`, `tenant_id`, `actor_id`, `event_type`, `entity_type`, `entity_id`, `timestamp`, `ip_context`, `metadata`, `result` | System-generated audit trail. | No. | No, but admin review may be required for exceptions. | Searchable by admins and owners only. | Tenant-scoped; operational staff access requires strict service controls. | `audit_events`; append-only table with RLS and retention policy. |

## Promotion Flows

### Subject From Purchase Appraisal to Sale Comparable

A subject property from a purchase appraisal can become a sale comparable only after explicit promotion:

1. The assignment and subject property are verified by an appraiser.
2. The purchase transaction details are entered or suggested as a candidate sale record.
3. The appraiser verifies sale date, price, property rights, financing, conditions of sale, buyer/seller treatment, and source support.
4. A `Verification Record` promotes the candidate to verified `Sale Comparable`.
5. The comp becomes firm-searchable only within the same tenant and only while freshness policy allows it.

The original assignment remains distinct from the sale comparable. The comp record should reference the source assignment and verification record for provenance.

### Newly Signed Leases to Lease Comparables

Newly signed leases can become lease comparables through controlled verification:

1. A lease is identified from approved user entry, a future source document workflow, or assignment data.
2. The lease candidate records tenant, space, commencement date, rent, term, escalations, concessions, expense structure, and source.
3. An appraiser verifies confidentiality, permission to reuse, and market relevance.
4. The candidate is promoted to verified `Lease Comparable`.
5. Firm search shows the lease comp only within the tenant and with stale-date warnings.

Confidential tenant names or deal terms may require restricted visibility even inside the firm.

### Saved Report Data to Market Indicators

Saved report data can become market indicators only after aggregation and review:

1. Verified assignments, comps, and report-derived facts are selected under tenant policy.
2. Candidate indicators are generated from approved structured fields, not raw report text.
3. Appraisers review market, date range, property type, sample size, outliers, and source count.
4. A `Verification Record` promotes the indicator to verified status.
5. The indicator becomes firm-searchable within the tenant, with date range and stale-date controls.

Market indicators must not expose confidential assignment-specific details unless the firm explicitly permits that use.

## Stale Comp Guardrails

Stale comp misuse should be prevented by policy and interface controls:

- Every comparable and market indicator should have `effective_date`, `verified_at`, and `stale_after` fields where applicable.
- Search results should surface freshness warnings before selection.
- Stale records should require reviewer acknowledgment or reverification before use.
- Verification should capture source date, confirmation date, and reviewer/appraiser identity.
- Reused comps should preserve original context, including property rights, conditions of sale, market conditions, and intended use.
- Records rejected or superseded by newer evidence should not appear in normal comp search.
- Tenant policy should define default stale thresholds by property type, market, and evidence type.

## No Cross-Firm Data Mixing

All intelligence records are tenant-scoped. The future database must enforce no cross-firm mixing through:

- Required `tenant_id` on every table containing firm-owned or derived intelligence.
- Row-level security for every tenant-scoped table.
- Tenant-scoped indexes, search filters, and future vector stores if ever approved.
- No shared comp vault across firms during the Continental-first pilot.
- No use of one firm's verified records to populate another firm's suggestions.
- Aggregate product analytics only when de-identified, non-confidential, and separated from firm-owned intelligence.

## Current Guardrail

This data model does not permit extraction. The current repository still supports metadata-only scanning, local manifests, metadata search, and assignment discovery. Real report contents must not be read, copied, parsed, summarized, embedded, or ingested until a separate approval gate is documented and implemented.

See `docs/verified-intelligence-workflow.md` for the future human-in-the-loop verification workflow.
See `docs/verified-intelligence-extraction-pipeline.md` for the future extraction-to-verification pipeline.
See `docs/data-confidence-provenance-model.md` for trust, evidence, and data passport rules.
See `docs/falcon-order-intelligence-loop.md` for order, assignment, and intelligence feedback-loop mapping.
