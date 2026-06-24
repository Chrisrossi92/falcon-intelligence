# Verified Intelligence Extraction Pipeline

This document designs the first human-approved extraction workflow for Falcon Intelligence. It is documentation-only and does not authorize extraction code, report reading, OCR, embeddings, copying files, or ingestion of real appraisal reports.

The pipeline describes how one completed appraisal assignment can move from metadata discovery into verified, tenant-scoped firm intelligence after explicit human approval.

## Overall Pipeline

### 1. Assignment Discovery

The workflow begins with metadata-only assignment discovery. Falcon uses saved scan manifests to identify probable assignment folders from filenames, extensions, relative paths, counts, and folder patterns.

Output:

- Candidate assignment folders.
- Heuristic labels.
- Completeness scores.
- Counts for PDFs, Word files, Excel files, photos, and map/images.

No source file contents are read in this stage.

### 2. Assignment Profile

An authorized user selects one discovered assignment folder and builds a metadata-only assignment profile.

Output:

- Assignment folder.
- Heuristic label.
- Completeness score.
- File groups for report candidates, workbook candidates, media candidates, PDF/source-document candidates, and other files.

The assignment profile becomes the review packet for deciding whether the assignment is eligible for a future extraction queue.

### 3. Extraction Queue

The extraction queue is a controlled future queue of assignment profiles approved for extraction review.

Queue entry requirements:

- Tenant ID.
- Assignment profile ID or saved profile reference.
- Selected source documents.
- Extraction phase target.
- Requesting user.
- Required reviewer/appraiser role.
- Allowed extraction scope.
- Explicit confirmation that extraction is approved for this assignment.

Queue status should include:

- `queued`
- `blocked`
- `extracting`
- `ready_for_human_review`
- `human_reviewing`
- `verified`
- `rejected`
- `archived`

### 4. AI Extraction

AI Extraction is a future controlled process that proposes structured fields from approved source documents. It should produce suggestions only.

Output:

- Suggested entity type.
- Suggested field name.
- Suggested raw value.
- Suggested normalized value.
- Extraction confidence.
- Provenance pointer.
- Extraction method/version.
- Warnings or conflicts.

AI Extraction must not promote data directly into verified firm intelligence.

### 5. Human Verification

An appraiser or approved reviewer compares each suggested field to source context. They may accept, edit, reject, defer, or request more evidence.

Human verification output:

- Verification status.
- Verified value.
- Verification confidence.
- Reviewer/appraiser notes.
- Field-level audit event.
- Source reference confirmation.

### 6. Reviewer Approval

Reviewer approval is a second control for fields or entity types that firm policy marks as sensitive, reusable, or QA-critical.

Reviewer approval should be required for:

- Reusable comparables.
- Market indicators.
- Historical comparable reuse.
- Fields with low extraction confidence.
- Fields that conflict with existing verified records.
- Stale or potentially stale evidence.

### 7. Intelligence Promotion

After human verification and any required reviewer approval, suggested data can be promoted into verified intelligence tables.

Promotion requirements:

- Verified status.
- Required role approval.
- Field-level provenance.
- Audit trail.
- Version snapshot.
- Tenant isolation checks.
- Searchability policy check.
- Stale-data policy check.

### 8. Searchable Knowledge Base

Verified intelligence becomes searchable only when the entity type, permission policy, confidentiality rules, tenant rules, and stale-data policy allow it.

Searchable data remains tenant-scoped. No verified field from one firm can populate another firm's knowledge base or suggestions.

## Extraction Targets by Phase

### Phase 1: Initial Safe Targets

Phase 1 should focus on low-risk assignment and report context fields. It should not extract comparables, values, rent conclusions, market conclusions, or narrative content.

Targets:

- Subject Property.
- Assignment metadata.
- Report metadata.

Candidate fields:

- Assignment identifier or folder label.
- Client or internal assignment label when approved.
- Property address.
- Property type.
- Effective date.
- Report date.
- Appraiser name.
- Reviewer name.
- Report type.
- Source document references.
- Report section labels or page ranges.

Phase 1 output should remain suggested until appraiser approval.

### Phase 2: Comparable Evidence

Phase 2 introduces higher-risk market evidence after Phase 1 controls are proven.

Targets:

- Sale comparables.
- Lease comparables.
- Listings.

Required controls:

- Field-level source references.
- Appraiser approval before comp vault use.
- Reviewer approval for historical or stale records.
- Clear distinction between sale, lease, and listing evidence.
- Confidentiality controls for lease terms and participant names.
- Stale-date assignment by evidence type and market.

### Phase 3: Advanced Intelligence

Phase 3 covers derived or narrative-sensitive intelligence.

Targets:

- Market indicators.
- Expense data.
- Cost data.
- Narrative references.

Required controls:

- Aggregation policy for market indicators.
- Source-count thresholds.
- Outlier review.
- Expense category normalization.
- Cost source versioning.
- Narrative reference provenance.
- Explicit reviewer approval before firm-searchable promotion.

Narrative references should not become reusable report language without separate template and narrative-engine controls.

## Extraction Confidence vs Verification Confidence

Extraction confidence and verification confidence are separate concepts.

Extraction confidence:

- Generated by the extraction process.
- Measures how strongly the system believes it found and normalized a field.
- Depends on source clarity, model behavior, field pattern, and conflict detection.
- Is advisory only.
- Cannot make a field verified.

Verification confidence:

- Assigned by the human reviewer or appraiser.
- Reflects professional judgment after reviewing the source and context.
- Can override extraction confidence with explanation.
- Determines whether a field is safe for promotion, reuse, or search.
- Must be captured in the verification record.

Example:

- A field can have high extraction confidence but low verification confidence if the source is stale, ambiguous, or not appropriate for reuse.
- A field can have medium extraction confidence but high verification confidence if the appraiser confirms it from source context.

## Provenance Requirements

Every extracted field must retain provenance before it can be verified.

Required provenance:

- Tenant ID.
- Originating assignment ID or assignment profile reference.
- Source document ID.
- Source file metadata reference.
- Page, section, table, or location reference when extraction is approved.
- Extracted field name.
- Raw extracted value.
- Normalized value.
- Extraction method and version.
- Extraction timestamp.
- User or process that queued extraction.
- Reviewer/appraiser who verified the field.
- Verification timestamp.

Fields without sufficient provenance should remain suggested or blocked. They should not become firm-searchable.

## Field-Level Audit History

Every field should have an audit trail from suggestion through promotion.

Field-level events:

- Suggested.
- Edited.
- Accepted.
- Rejected.
- Deferred.
- Reopened.
- Reviewer approved.
- Promoted to verified intelligence.
- Marked stale.
- Archived.
- Restored.

Each event should capture:

- Actor.
- Role.
- Timestamp.
- Previous value.
- New value.
- Reason or note.
- Confidence values.
- Source reference.
- Entity and field identifiers.

Audit events should be append-only. Corrections should create new events rather than rewriting history.

## Stale-Data Policies

Stale-data policy should prevent old or context-specific evidence from being reused without review.

Default policy expectations:

- Every comparable should have an effective date or source date.
- Every verified comp should have `verified_at` and `stale_after`.
- Market indicators should have a date range and source count.
- Listings should stale faster than closed sales.
- Lease comps should be reviewed when market conditions, lease structure, or concession patterns change.
- Expense and cost data should stale based on expense year, source type, and market volatility.
- Search should display stale warnings before selection.
- Stale records should require appraiser justification before reuse.

Stale records are not necessarily wrong. They are context-sensitive and must be treated as requiring renewed judgment.

## Historical Comparable Workflow

Historical comparable reuse requires explicit appraiser justification before verified historical data is reused.

Workflow:

1. User selects a verified historical comparable.
2. Falcon checks stale policy, market, property type, date, source context, and prior verification record.
3. If stale or context-sensitive, Falcon routes the comp to appraiser justification.
4. The appraiser documents why the historical comp remains relevant.
5. Reviewer approval is required when firm policy marks the comp as high impact or stale.
6. A new audit event records reuse, justification, and any updated verification confidence.
7. The original comp remains unchanged; reuse context is recorded separately.

Required justification fields:

- Reason for reuse.
- Market condition relevance.
- Adjustments or limitations.
- Effective date context.
- Source reliability.
- Reviewer approval status when required.

## Origin Links for Verified Fields

Every verified field must remain linked to its originating assignment and supporting report.

Required links:

- `tenant_id`
- `assignment_id`
- `source_document_id`
- `report_section_id` when available.
- `verification_record_id`
- `audit_event_id`
- `field_version_id`

Promotion into firm-searchable intelligence should never detach a field from its assignment context. This protects provenance, stale review, and professional accountability.

## Future Falcon Integration

Future Falcon/Supabase integration should map the pipeline into tenant-scoped tables and services.

Candidate tables:

- `extraction_queue`
- `extraction_runs`
- `extracted_field_suggestions`
- `field_verifications`
- `field_versions`
- `verification_records`
- `audit_events`
- `source_documents`
- `assignments`
- `subject_properties`
- `sale_comparables`
- `lease_comparables`
- `listing_comparables`
- `market_indicators`

Integration requirements:

- Row-level security on every tenant-scoped table.
- Service-role operations limited to extraction jobs and logged.
- No cross-firm search indexes.
- No shared vector store unless a future policy explicitly approves a separate de-identified aggregate product dataset.
- Clear separation between suggested records and verified records.
- Search only over verified and policy-searchable records.
- Rejected records retained for audit but excluded from default search.

## Current Guardrail

This pipeline is a design document only. The current repository remains limited to metadata-only scanning, local manifests, metadata search, assignment discovery, and assignment profiles. No extraction code exists. No report contents should be read, copied, parsed, summarized, embedded, OCRed, or ingested.
