# Verified Intelligence Workflow

This document defines the future human-in-the-loop workflow for transforming metadata-discovered assignments into verified firm intelligence. It is documentation-only and does not authorize extraction, report reading, OCR, embeddings, copying files, or ingestion of real report contents.

## Intelligence Lifecycle

### Discovered

An assignment has been identified from metadata-only scan manifests and assignment discovery. At this stage Falcon knows only filenames, extensions, relative paths, counts, and heuristic labels. No report contents have been read.

### Ready for Extraction

An authorized user has selected a discovered assignment profile as a candidate for future controlled extraction. This state means the folder structure and metadata appear organized enough for review planning. It does not mean extraction has run.

### AI Suggested

Future extraction or AI assistance has proposed structured fields, comparable records, market indicators, report-section metadata, or reviewer notes. Suggested values are drafts only. They are not verified, not firm-searchable by default, and not eligible for comp vault use.

### Appraiser Reviewing

An appraiser or reviewer is actively comparing suggested fields against approved source context. They may edit values, add notes, reject fields, request additional verification, or promote fields to verified status.

### Verified

An authorized appraiser, reviewer, admin, or owner has approved the record under firm policy. Verified records may become firm-searchable when the entity type, confidentiality policy, stale-date policy, and tenant controls allow it.

### Rejected

A suggested record was reviewed and declined. Rejected data remains retained for auditability and model/process improvement review, but it is excluded from ordinary search, comp selection, market intelligence, and narrative workflows.

### Archived

An assignment, suggestion batch, or verified record has been retired from active workflows. Archived records remain auditable, but normal search and suggestion flows should hide them unless a user with appropriate permissions requests archive history.

## Verification UI Concept

The future verification workspace should use a three-panel review layout:

| Panel | Purpose | Contents |
| --- | --- | --- |
| Left: Source Document Preview | Shows the human reviewer where a suggested field came from after extraction is approved. | Local document preview, page reference, section reference, source-document metadata, and navigation controls. |
| Center: Extracted Fields | Presents proposed structured intelligence for review. | Field name, suggested value, normalized value, entity target, required/optional status, edit controls, accept/reject actions, and validation warnings. |
| Right: Confidence, Reviewer Notes, Audit History | Explains why the suggestion needs review and records decisions. | Confidence score, extraction method, reviewer notes, prior decisions, stale-data warnings, permission context, and audit events. |

Current prototype guardrail: this UI is a design target only. The repository does not preview source documents or extract report text today.

## Verification Permissions

| Role | Verification Responsibilities |
| --- | --- |
| Admin | Configures verification policies, stale thresholds, role access, source eligibility, and searchability rules. Can manage queues but should not bypass required appraiser approval for valuation facts. |
| Appraiser | Primary authority for verifying assignment facts, subject data, comparables, report-derived market indicators, and reusable intelligence. Can approve, edit, reject, or archive suggestions within assigned scope. |
| Reviewer | Reviews QA-sensitive fields, flags inconsistencies, confirms reviewer notes, and may verify records when firm policy allows reviewer approval. Can request changes or require appraiser confirmation. |
| Owner | Controls tenant-level policy, module enablement, data retention, cross-module search settings, and final escalation decisions. Has audit visibility across the tenant. |

Default posture:

- Suggested intelligence is not trusted until approved.
- Verification authority is tenant-scoped.
- Client-facing users do not verify internal intelligence.
- No role can move data across firm boundaries.

## Confidence Scoring Philosophy

Confidence scores should support review priority, not replace human judgment.

Principles:

- Confidence is advisory, never determinative.
- Low confidence should route suggestions to careful review or rejection.
- High confidence should still require approval for valuation facts, comps, market indicators, and reusable firm intelligence.
- Confidence should reflect source quality, field clarity, extraction consistency, normalization reliability, and conflicting evidence.
- Confidence should degrade when source documents are stale, ambiguous, incomplete, or unsupported.
- Confidence should be visible with explanation, not a black-box number alone.

Future confidence levels may include:

- `high`: clear source support and consistent normalization.
- `medium`: plausible but needs ordinary review.
- `low`: uncertain, conflicting, stale, or incomplete.
- `blocked`: cannot be reviewed without additional source context.

## Audit Trail

Every verification-relevant event should create an audit event.

Audit events should capture:

- Tenant ID.
- Actor and role.
- Timestamp.
- Assignment or entity reference.
- Previous status and new status.
- Field-level changes when applicable.
- Source document reference.
- Confidence score at time of decision.
- Reviewer notes or rejection reason.
- Searchability changes.
- Archive or restore action.

Audit history should be append-only. Corrections should create new events rather than rewriting prior history.

## Version History

Verified intelligence should support version history so the firm can see how records changed over time.

Version records should capture:

- Entity type and entity ID.
- Version number.
- Snapshot of approved structured fields.
- Verification status.
- Verifier identity.
- Effective date or source date.
- Reason for change.
- Superseded-by relationship when a newer record replaces an older one.

Version history should protect against stale comp misuse by preserving the context in which a record was originally verified.

## How Verified Data Becomes Searchable

Verified data becomes searchable only after all required gates pass:

1. Entity status is `verified`.
2. Tenant policy permits the entity type to be searchable.
3. Required permissions allow the current user to see the entity.
4. Confidentiality restrictions allow reuse.
5. Stale-date policy does not block ordinary use.
6. Source provenance and verification record are present.

Search indexes must remain tenant-scoped. Future vector stores, if ever approved, must also be tenant-scoped and must not mix firm data.

## How Rejected Data Is Retained but Excluded

Rejected data should be retained for accountability while staying out of normal workflows.

Rejected records should:

- Keep source references and reviewer rationale.
- Remain visible in audit and exception review views.
- Be excluded from default firm search.
- Be excluded from comp vault selection.
- Be excluded from market indicator generation.
- Be excluded from narrative and template workflows.
- Require admin or owner permission for bulk review or restoration.

Restoring rejected data should create a new audit event and usually require a fresh verification review.

## Future Falcon Integration

In a future Falcon/Supabase architecture, the workflow should map to:

- `assignments` for assignment context.
- `source_documents` for metadata and approved source references.
- `verification_records` for suggested, verified, rejected, and archived decisions.
- `reviewer_notes` for human review commentary.
- `audit_events` for immutable event history.
- Entity tables such as `sale_comparables`, `lease_comparables`, `market_indicators`, and `subject_properties` for verified intelligence.

Supabase row-level security should enforce tenant isolation for every workflow table. Service-role actions should be narrow, logged, and limited to specific background jobs.

## Current Guardrail

This workflow is a design document only. Falcon Intelligence currently supports metadata-only scanning, local manifests, metadata search, assignment discovery, and assignment profile export. It does not read report contents, preview source documents, extract text, create embeddings, run OCR, or ingest real appraisal reports.

See `docs/verified-intelligence-extraction-pipeline.md` for the future human-approved extraction pipeline design.
See `docs/data-confidence-provenance-model.md` for the future confidence and provenance model.
