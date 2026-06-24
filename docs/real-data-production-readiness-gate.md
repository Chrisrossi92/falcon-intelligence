# Real Data Production Readiness Gate

This checklist must be satisfied before Falcon Intelligence may process real appraisal report content, source-document content, extraction output, OCR output, embeddings, source-document preview, or client/report-derived reusable intelligence.

Until this gate passes, only metadata-only real-data scans are allowed. Content extraction is blocked.

## Current Rule

Metadata-only real-data scans are allowed when they follow the existing scanner boundary:

- File names.
- Extensions.
- Relative paths.
- Sizes.
- Timestamps.
- Counts and simple metadata summaries.

Blocked until this gate passes:

- Reading report body text.
- Parsing PDFs, DOCX, XLSX, CSV, TSV, images, or email attachments for content.
- OCR.
- Embeddings or vector stores.
- Source-document preview.
- Copying source files into the repository.
- Persisting extracted fields from real reports.
- Training, fine-tuning, or improving models on client/report data.

## Required Approvals

Legal/company approval must be documented before real content work starts.

Required signoffs:

- Company owner or executive sponsor.
- Legal/privacy reviewer.
- Appraisal compliance lead.
- Security/IT owner.
- Product owner for Falcon and Falcon Intelligence.
- Engineering owner responsible for implementation and rollback.

Approvals must identify:

- Approved data types.
- Approved tenants or pilot groups.
- Approved environments.
- Approved users and roles.
- Allowed retention period.
- Whether source preview is allowed.
- Whether extraction output may be persisted.
- Whether any third-party service is involved.

No approval may be implied from local development convenience or user access to a drive.

## Tenant Isolation Requirements

Before real content work:

- Every record must include `tenant_id`.
- Row-level security or equivalent tenant enforcement must exist.
- Cross-tenant search must be disabled by default.
- Service-role access must be limited, logged, and reviewed.
- Test tenants must be clearly separated from production tenants.
- Backups and logs must preserve tenant boundaries.
- Any shared analytics must be aggregated and de-identified.

## Data Retention Rules

Retention policy must be explicit before content is processed.

Required decisions:

- Whether source files are ever copied.
- Whether extracted text is stored.
- Whether OCR output is stored.
- Whether embeddings are stored.
- Whether source previews are cached.
- How long each artifact is retained.
- How deletion requests are handled.
- How superseded or rejected facts are retained for audit.

Default stance:

- Do not copy source files.
- Do not store extracted text unless approved.
- Do not store embeddings unless approved.
- Keep audit logs append-only, subject to firm policy and legal requirements.

## Confidentiality and USPAP Guardrails

Falcon Intelligence must preserve appraisal confidentiality and professional responsibility.

Guardrails:

- Client-facing users must not see internal firm intelligence unless explicitly approved.
- Confidential assignment results, comp details, lease terms, and workfile material must remain role-scoped.
- Appraiser remains responsible for relevance, selection, verification, adjustment, and final conclusions.
- Intelligence is assistive and must not automatically create valuation conclusions.
- Every surfaced fact must remain traceable to source, verification, reviewer status, and audit history.
- Historical or stale comps require visible warnings and appraiser justification before reuse.
- Generated or reusable narrative must be reviewed by an appraiser before report use.

## Permission Model Requirements

Production permission checks must exist before content access.

Required controls:

- Tenant membership.
- Company/tenant role.
- Order or assignment access.
- Evidence visibility level.
- Source-document confidentiality.
- Reviewer/admin override policy.
- Client-access exclusion for internal intelligence.
- Explicit denial for disabled evidence links.

The local `permission_policy.py` scaffold is not production auth. It may guide role names and expected decisions, but production must enforce permissions through the real Falcon identity and data-access layer.

## Audit Persistence Requirements

Suggested audit payloads are not enough for production.

Before real content access:

- Audit events must be durably persisted.
- Audit writes must be append-only.
- Audit events must include tenant, order, user, role, action, timestamp, target IDs, result, and relevant justification.
- Evidence opened, passport viewed, fact selected, fact rejected, fact overridden, and historical comp justification events must be logged.
- Failed or denied access attempts must be logged where policy requires.
- Audit logs must be queryable for compliance review.

## Evidence Viewer Requirements

No source-document preview is allowed until the viewer is explicitly approved.

Viewer requirements:

- Permission check before opening any evidence.
- Tenant and assignment scope enforcement.
- No raw absolute path exposure in UI.
- No uncontrolled file copy.
- Clear distinction between metadata-only evidence and content preview.
- Bounded snippets only when source-preview policy approves them.
- Redaction strategy for sensitive fields where required.
- Audit event when evidence is opened.
- Safe unavailable states for missing, disabled, or permission-denied evidence.

## Human Verification Requirements

Extracted or suggested facts must not become trusted intelligence automatically.

Required lifecycle:

- Suggested.
- Appraiser review.
- Verified, edited, rejected, or deferred.
- Reviewer approval when policy requires.
- Searchable only after provenance, permission, freshness, and verification checks pass.

Every verified fact must retain:

- Source assignment.
- Source document or evidence link.
- Verification status.
- Verifier and timestamp.
- Reviewer and timestamp where applicable.
- Confidence dimensions.
- Audit references.
- Stale or conflict warnings where applicable.

## Model Training Rule

Client/report data must not be used for model training, fine-tuning, evaluation datasets, prompt libraries, or vendor improvement programs unless a separate written company/legal approval explicitly authorizes that use.

Default rule:

- No model training on client data.
- No model training on report data.
- No model improvement opt-in for third-party vendors.
- No report-derived examples in public or shared prompts.

## Real-Data Testing Approval Process

Before any test touches real content:

1. Write a test plan describing data, users, scope, environment, retention, and rollback.
2. Confirm legal/company approval.
3. Confirm tenant and permission controls.
4. Confirm audit persistence.
5. Confirm no repository commits can include source files or extracted content.
6. Use the smallest approved data set.
7. Run in an approved environment.
8. Review logs and outputs for leakage.
9. Document results and cleanup.
10. Do not expand scope without renewed approval.

Synthetic fixtures remain the default for automated tests.

## Allowed Action Matrix

| Action | Status | Notes |
| --- | --- | --- |
| Scan file metadata from a user-selected local folder | Green | Allowed when metadata-only and no content is read. |
| Search metadata manifests | Green | Allowed when manifest contains no extracted source content. |
| Use committed synthetic fixtures | Green | Allowed for tests, demos, and CI. |
| Generate synthetic UI cards, passports, evidence summaries, and audit payloads | Green | Allowed when based only on synthetic fixtures. |
| Display real source file names and metadata internally | Yellow | Requires tenant/user permission and no source content preview. |
| Store real metadata manifests outside the repository | Yellow | Requires retention and access policy. |
| Preview real source documents | Red | Blocked until evidence viewer requirements pass. |
| Extract text from real reports or workfiles | Red | Blocked until this gate passes. |
| Run OCR on real documents or images | Red | Blocked until this gate passes. |
| Create embeddings from real content | Red | Blocked until this gate passes. |
| Persist extracted real report facts | Red | Blocked until verification, provenance, audit, and retention controls pass. |
| Train or fine-tune models on client/report data | Red | Blocked unless separately approved in writing. |
| Commit real reports, source documents, extracted text, OCR output, embeddings, or exports | Red | Always prohibited. |

## Gate Exit Criteria

This gate passes only when:

- All required approvals are documented.
- Tenant isolation is implemented and tested.
- Permission checks are implemented and tested.
- Audit persistence is implemented and tested.
- Evidence viewer policy is approved and tested if preview is in scope.
- Retention and deletion behavior is documented and tested.
- Human verification workflow is implemented and tested.
- CI and repository safety checks prevent accidental content commits.
- Rollback and incident response steps are documented.

Until all applicable criteria are met, keep Falcon Intelligence synthetic-first and metadata-only.
