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

The current synthetic/local evidence link model lives in `src/falcon_intel/evidence_link.py`. It defines stable metadata-only link objects for future "open source report" and "jump to evidence" behavior. These objects are safe placeholders, not file openers.

Current evidence link fields:

- `evidence_id`
- `tenant_id`
- `assignment_id`
- `source_document_id`
- `source_document_type`
- `display_label`
- `access_level`
- `future_page_number`
- `future_section_anchor`
- `future_highlight_text`
- `status`

Stable access-level codes:

- `internal_only`
- `appraiser_reviewer_only`
- `owner_admin_only`
- `disabled`

Supported synthetic source-document types:

- `source_report`
- `source_document`
- `comparable_support`
- `market_support`

The `future_page_number`, `future_section_anchor`, and `future_highlight_text` fields are future-facing anchors only. They must not be populated from real report text until a controlled extraction and source-preview policy is approved.

Access-controlled opening rules should consider:

- Tenant membership.
- Assignment access.
- Role permission.
- Source document confidentiality.
- Whether source preview is enabled for the deployment.
- Whether the local file still exists at an approved location.
- Whether the action is logged.

## Permission Policy Scaffold

The current synthetic/local permission policy scaffold lives in `src/falcon_intel/permission_policy.py`. It is not production authentication or authorization. It is a stable decision matrix for future Falcon UI/API wiring and tests.

Stable role codes:

- `owner`
- `admin`
- `appraiser`
- `reviewer`
- `trainee`
- `client`

Supported permission checks:

- `can_view_intelligence_card`
- `can_view_passport_detail`
- `can_open_evidence_link`
- `can_verify_fact`
- `can_review_fact`
- `can_override_fact`
- `can_archive_fact`

Decisions return:

- `allowed`
- `reason_code`
- `reason_label`

Client users are always denied access to internal Falcon Intelligence. Evidence decisions respect `internal_only`, `appraiser_reviewer_only`, `owner_admin_only`, and `disabled` access levels. Production Falcon must replace or wrap this scaffold with real tenant membership, role assignment, order access, and audit persistence.

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

The current synthetic/local data passport model lives in `src/falcon_intel/data_passport.py`. It is a structured trust-card payload only; it does not read source documents, open files, extract text, run OCR, or create embeddings.

Current data passport fields:

- `fact_id`
- `tenant_id`
- `assignment_id`
- `fact_type`
- `display_label`
- `display_value`
- `verification_status`
- `verified_by`
- `verified_at`
- `reviewed_by`
- `reviewed_at`
- `confidence_dimensions`
- `evidence_links`
- `audit_event_ids`
- `searchable_status`

Current confidence dimension fields:

- `extraction_confidence`
- `source_quality`
- `source_agreement`
- `freshness`
- `reviewer_approval`
- `historical_consistency`

The `evidence_links` field uses the synthetic/local evidence link model described above. In the current prototype, a passport explains provenance through IDs, labels, confidence dimensions, and evidence metadata only. It must not contain real client names, report text, absolute paths, OneDrive paths, or source-file contents.

## Card Summary vs Passport Detail

The Firm Intelligence Found card should remain a concise routing surface. Top match rows may show only data passport summary fields:

- `passport_id`
- `verification_status`
- `evidence_link_count`
- `confidence_summary`
- `searchable_status`

Full passport objects, confidence dimensions, evidence link arrays, audit IDs, and future page/section anchors belong in a dedicated passport or evidence detail drawer. This keeps the card readable and prevents broad exposure of source metadata before a user explicitly opens the supporting provenance view.

The current synthetic detail lookup uses committed fixture records at:

```text
tests/fixtures/synthetic_data_passports/data-passports.json
```

`lookup_data_passport_detail` accepts `tenant_id` and `passport_id`, then returns a safe local response:

- `found`: includes the full synthetic passport detail.
- `not_found`: no passport body is returned.
- `error`: validation or fixture failure, with a short error message.

The lookup is local and in-memory only. It is not a web API, database query, source-document opener, report parser, extraction pipeline, or permission engine.

For Falcon-style integration tests, `build_falcon_passport_detail_response` wraps this lookup with `tenant_id`, `order_id`, `user_id`, and `passport_id`. A found response includes a suggested `opened_evidence` audit event for the future detail drawer interaction. Falcon remains responsible for permission checks and durable audit persistence in production.

The future Falcon passport detail drawer has a versioned synthetic UI contract snapshot at:

```text
tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json
```

The drawer schema is produced by `build_passport_detail_drawer` and includes `schema_version`, passport identity, fact summary, verification/review summary, confidence dimensions, evidence link summaries, audit event IDs, searchable status, and warnings. It intentionally summarizes evidence links and does not open source files or include report contents.

When a user selects an evidence row from the drawer, `build_falcon_evidence_open_response` verifies that the synthetic `evidence_id` belongs to the requested `passport_id`. A successful response returns a metadata-only evidence summary and a suggested `opened_evidence` audit event. It must not open files, read report contents, or expose source text.

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

See `docs/falcon-order-intelligence-loop.md` for how verified intelligence may surface in future Falcon order workflows.
