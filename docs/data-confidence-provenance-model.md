# Data Confidence and Provenance Model

This document defines how Falcon Intelligence should make verified data trustworthy. It is documentation-only and does not authorize extraction code, source-file reading, OCR, embeddings, copying files, or ingestion of real report contents.

Trust in Falcon Intelligence should come from visible provenance, human verification, freshness controls, conflict detection, and tenant-scoped auditability.

## Data Confidence Dimensions

Confidence should be multi-dimensional. A single score is not enough to decide whether appraisal intelligence can be trusted or reused.

| Dimension | Meaning | Primary Question | Example Signals |
| --- | --- | --- | --- |
| Extraction confidence | System confidence that a suggested field was found and normalized correctly. | Did the extraction process identify the field clearly? | Source clarity, field pattern match, normalization quality, model agreement, extraction warnings. |
| Verification status | Human-reviewed lifecycle state. | Has an authorized person approved this field? | Suggested, appraiser reviewing, verified, rejected, archived. |
| Source quality | Reliability of the source supporting the field. | Is the source appropriate for this field? | Final report, signed lease, verified sale confirmation, draft document, user-entered note, public listing. |
| Source agreement | Consistency across available sources. | Do multiple sources support the same value? | Matching report section and workbook value, conflicting sale price, inconsistent lease term. |
| Data freshness | Age and market relevance of the field. | Is this data still current enough to reuse? | Effective date, verification date, stale-after date, market volatility, listing status. |
| Reviewer approval | Secondary approval for sensitive or reusable intelligence. | Has the field passed required review controls? | Reviewer sign-off, requested changes, override notes, QA approval. |
| Historical consistency | Alignment with prior verified records. | Does this match the firm's historical record for the same property or comp? | Prior GLA, prior sale price, prior lease term, superseded records, known corrections. |

Confidence display should show these dimensions separately before any combined trust indicator is shown.

## Evidence Links

Every trusted field should provide evidence links that let an authorized user understand where the value came from.

Evidence link types:

- Source report link: link to the originating report record or source document metadata.
- Source document link: link to the tenant-scoped source document record.
- Future page/section anchor: page, section, table, exhibit, or paragraph location once controlled extraction is approved.
- Future highlighted evidence snippet: a bounded preview of the supporting passage after source-preview policy is approved.
- Access-controlled opening rules: checks that decide whether a user can open the underlying local or managed source.

Evidence links should be metadata-first. In the current prototype, evidence should point to manifest/profile/source metadata only, not report contents.

Access-controlled opening rules should consider:

- Tenant membership.
- Assignment access.
- Role permission.
- Source document confidentiality.
- Whether source preview is enabled for the deployment.
- Whether the local file still exists at an approved location.
- Whether the action is logged.

## Data Passport Concept

A data passport is the visible trust card for one verified field or intelligence record.

Each passport should answer:

- Where did this come from?
- Who verified it?
- When was it verified?
- Who reviewed it?
- What changed?
- Why is it searchable?

Recommended passport fields:

- Entity type and entity ID.
- Field name.
- Verified value.
- Original suggested value.
- Source assignment.
- Source report or source document.
- Page/section anchor when available.
- Extraction confidence.
- Verification confidence.
- Verification status.
- Verifier identity and timestamp.
- Reviewer identity and timestamp.
- Last changed by and change reason.
- Stale-after date.
- Searchability reason.
- Tenant ID.
- Audit event references.

The passport should be available anywhere a user sees verified intelligence, especially comp selection, market indicator search, and narrative support views.

## Historical Comparable Workflow

Historical comparables can be useful, but they require explicit context before reuse.

Workflow:

1. User selects a verified historical comparable.
2. Falcon shows an age warning based on effective date, verification date, stale-after date, and market policy.
3. Falcon displays the data passport and supporting evidence links.
4. Appraiser enters required justification for reuse.
5. Reviewer approval is requested when policy requires it.
6. Falcon records an audit event for the reuse decision.
7. If reused in a report, Falcon stores reusable explanation text for report comments.

Required appraiser justification:

- Why the historical comparable remains relevant.
- Market condition context.
- Property similarity or difference.
- Adjustment considerations.
- Limitations or caveats.
- Whether additional verification was performed.

Reusable explanation text should be generated or drafted only from approved structured fields and appraiser-provided justification. It should not rely on unverified report text.

Audit record should capture:

- User.
- Role.
- Comparable ID.
- Assignment using the comp.
- Age warning shown.
- Justification text.
- Reviewer approval status.
- Timestamp.

## Conflict Detection

Conflict detection should identify records that need review before reuse.

Conflict types:

- Same property conflicting GLA.
- Different sale prices for the same transaction.
- Mismatched lease terms.
- Conflicting dates.

Conflict detection should compare:

- Current suggested field against verified records.
- Newly verified field against historical versions.
- Multiple source documents in the same assignment.
- Comparable records tied to the same property.
- User edits against extracted suggestions.

Conflict states:

- `no_conflict`: no material conflict found.
- `needs_review`: possible mismatch requiring human review.
- `confirmed_difference`: different values are valid due to context.
- `resolved`: conflict reviewed and corrected or accepted.
- `superseded`: older value replaced by newer verified value.

Examples:

- Same property conflicting GLA: require appraiser to identify whether the difference is measurement basis, building change, data error, or source limitation.
- Different sale prices: require source comparison and transaction context before comp use.
- Mismatched lease terms: require review of commencement date, term, rent basis, concessions, and expense structure.
- Conflicting dates: require clarification of effective date, report date, sale date, lease date, and verification date.

Conflicts should not automatically reject a record. They should route it to human review and preserve the decision trail.

## Firm-Level Confidence Dashboard

The firm-level dashboard should show the health of verified intelligence without exposing unauthorized report contents.

Dashboard sections:

- Verified records: count by entity type, property type, market, appraiser, and date range.
- Needs review: suggestions awaiting appraiser or reviewer action.
- Stale/historical records: records past stale policy or requiring reuse justification.
- Conflicting records: unresolved field conflicts by type and severity.
- Recently verified records: latest verified assignments, comps, indicators, and property facts.

Useful metrics:

- Verification throughput.
- Average time from suggestion to verification.
- Rejection rate by extraction target.
- Conflict rate by entity type.
- Stale comp reuse count.
- Reviewer override count.
- Records searchable vs restricted.

The dashboard should be tenant-scoped and role-filtered.

## Permissions

Permissions should separate evidence visibility, verification authority, override authority, and archive authority.

| Permission Area | Owner | Admin | Appraiser | Reviewer |
| --- | --- | --- | --- | --- |
| View evidence links | Yes, tenant-wide unless restricted by policy. | Yes, operational scope. | Yes, assigned matters and permitted firm intelligence. | Yes, review scope. |
| Verify fields | Policy-dependent, generally escalation only. | Configuration and admin records; valuation facts require appraiser authority. | Yes, for assigned or permitted valuation facts. | Yes, when firm policy permits reviewer verification. |
| Override confidence or stale warnings | Yes, with audit event. | Yes for policy/admin overrides; valuation overrides should require appraiser/reviewer input. | Yes for professional judgment fields with justification. | Yes for QA/review scope with notes. |
| Archive records | Yes. | Yes within operational policy. | Yes for assigned matter records if policy permits. | Yes for review records if policy permits. |

Client users should not verify internal intelligence, override confidence, or access internal evidence links unless the firm explicitly shares a narrow deliverable.

All permission-sensitive actions should create audit events.

## Future Falcon/Supabase Implementation Notes

Candidate tables:

- `data_passports`
- `evidence_links`
- `confidence_dimensions`
- `field_conflicts`
- `historical_reuse_justifications`
- `firm_confidence_dashboard_snapshots`
- `verification_records`
- `field_versions`
- `audit_events`

Implementation requirements:

- Every table containing firm intelligence must include `tenant_id`.
- Row-level security must enforce tenant isolation.
- Evidence links must check source-document permissions before opening.
- Highlighted snippets should be stored or generated only after extraction and preview policies are approved.
- Search indexes should include only verified and policy-searchable records.
- Rejected and archived records should remain queryable only through audit or exception views.
- Service-role actions should be narrow, logged, and reviewed.
- No cross-firm confidence aggregation should expose firm-owned intelligence.

## Current Guardrail

This model is a trust and provenance design only. Falcon Intelligence currently supports metadata-only scanning, local manifests, metadata search, assignment discovery, and assignment profile export. It does not read report contents, extract text, OCR documents, create embeddings, copy files, or ingest appraisal reports.
