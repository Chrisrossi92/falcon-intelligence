# Production Gate Review Packet Template

This packet must be completed, reviewed, and approved before any pilot may process real appraisal report content, source-document content, extraction output, OCR output, embeddings, or source-document preview.

This template does not authorize real data access, OneDrive access, report parsing, extraction, OCR, embeddings, source-document preview, model training, or ingestion. Until the packet is approved, Falcon Intelligence remains synthetic-first and metadata-only.

## 1. Pilot Scope

Complete before review:

- Pilot name:
- Requesting owner:
- Business objective:
- Tenant/company:
- Approved environment:
- Start date:
- End date:
- Maximum number of folders:
- Maximum number of assignments:
- Maximum number of reports:
- Whether source-document preview is requested:
- Whether extracted content may be persisted:
- Whether embeddings are requested:
- Whether any third-party service is involved:

Scope statement:

```text
Describe exactly what the pilot will do, what it will not do, and why the smallest possible scope is sufficient.
```

## 2. Approver Checklist

Every approval must include approver name, role, date, and explicit approval notes.

| Approval | Required approver | Status | Notes |
| --- | --- | --- | --- |
| Company owner approval | Company owner or executive sponsor | Not started |  |
| Legal/confidentiality review | Legal or privacy reviewer | Not started |  |
| USPAP/confidentiality review | Appraisal compliance lead | Not started |  |
| Tenant isolation review | Engineering/security owner | Not started |  |
| Security/access review | Security/IT owner | Not started |  |
| Audit logging review | Compliance or engineering owner | Not started |  |
| Rollback plan approval | Product and engineering owners | Not started |  |

No approval may be inferred from drive access, local development convenience, or prior synthetic validation.

## 3. Data Scope

Allowed folders:

```text
List exact approved folder roots or controlled pilot locations. Do not include broad drive roots.
```

Excluded folders:

```text
List folders that must not be scanned, previewed, extracted, copied, indexed, or embedded.
```

Allowed file types:

```text
List approved file extensions and whether they are metadata-only, preview-eligible, extraction-eligible, OCR-eligible, or embedding-eligible.
```

Prohibited data types:

- Client-visible deliverables outside the approved tenant/order scope.
- Personal user files.
- Human resources, legal, billing, or administrative files.
- Third-party confidential data outside the approved assignment scope.
- Any source document not listed in the approved folder/file scope.
- Any file type not explicitly approved above.

Metadata-only vs content extraction:

| Activity | Definition | Pilot status |
| --- | --- | --- |
| Metadata-only scan | Reads file names, extensions, relative paths, sizes, timestamps, and counts only. | Allowed only inside approved scope. |
| Source-document preview | Opens or renders document contents for a user. | Blocked unless explicitly approved. |
| Content extraction | Reads or parses report/workfile contents into text, fields, comps, sections, or summaries. | Blocked unless explicitly approved. |
| OCR | Converts images or scanned documents into text. | Blocked unless explicitly approved. |
| Embeddings | Creates vector representations from report/client/source content. | Blocked unless explicitly approved. |

## 4. Authorized Pilot Roles

List named users and roles authorized for the pilot.

| User | Falcon role | Pilot responsibility | Authorized actions | Restrictions |
| --- | --- | --- | --- | --- |
|  | owner/admin/appraiser/reviewer/trainee |  |  |  |

Required defaults:

- Client users are not authorized for internal intelligence.
- Trainee users may participate only when explicitly supervised.
- Service-role or automation access must be logged and scoped to the pilot.
- Admin access does not bypass appraisal review, confidentiality, or audit requirements.

## 5. Test Plan

Required sequence:

1. Synthetic fallback: verify the current synthetic validation suite passes before any real-data pilot step.
2. Small folder first: run only metadata checks against the smallest approved folder.
3. One assignment first: validate tenant, permission, audit, rollback, and output review on one approved assignment.
4. One report first: if content extraction or preview is approved, test only one approved report before expanding.
5. Review outputs: confirm no prohibited data, cross-tenant leakage, raw path exposure, uncontrolled source text, or client-visible intelligence appears.
6. Decide whether to continue, pause, or roll back.

Required preflight checks:

- Repository safety checks pass.
- CI synthetic validation passes.
- Tenant isolation test passes.
- Permission-denied paths are tested.
- Audit persistence is tested.
- Rollback process is rehearsed.
- Synthetic fallback remains available.

## 6. Rollback Plan

Rollback owner:

Rollback trigger conditions:

- Unauthorized folder or file encountered.
- Tenant isolation failure.
- Permission bypass or incorrect access decision.
- Audit event not persisted.
- Source preview opens outside approved scope.
- Extracted content appears in an unauthorized location.
- Any real report/client content is committed to git.
- User reports confidentiality, USPAP, or client-visibility concern.

Rollback steps:

1. Stop the pilot job or disable the feature flag.
2. Revoke pilot access for affected users or service roles.
3. Preserve audit logs and incident notes.
4. Remove unauthorized derived artifacts according to retention policy.
5. Verify no prohibited files or extracted content were committed.
6. Notify required approvers.
7. Document root cause and corrective action before resuming.

## 7. Success Criteria

The pilot is successful only if all applicable criteria are met:

- No real report, source document, extracted text, OCR output, embedding, vector store, CSV/TSV export, PDF, DOCX, XLSX, or client file is committed to the repository.
- Tenant isolation is enforced and tested.
- Client users cannot see internal intelligence.
- Authorized users can complete the approved workflow.
- Denied users receive safe denied states.
- Every preview, extraction, selected fact, rejected match, and historical comp justification is auditable.
- Appraiser review remains required before reuse.
- No automatic valuation conclusion is generated.
- Rollback can be completed within the approved response window.
- Outputs are traceable, minimal, and limited to approved scope.

## 8. Red/Yellow/Green Pilot Matrix

| Action | Status | Conditions |
| --- | --- | --- |
| Use synthetic fixtures and snapshots | Green | Always allowed for local tests and CI. |
| Metadata-only scan of approved pilot folder | Green | Allowed only within exact approved scope. |
| Store real metadata manifest outside repository | Yellow | Requires retention, access, and tenant controls. |
| Internal metadata-only intelligence card | Yellow | Requires tenant, role, and audit controls. |
| Source-document preview for one approved report | Yellow | Requires viewer approval, permission checks, and audit persistence. |
| Content extraction for one approved report | Yellow | Requires full packet approval, human verification, retention policy, and rollback plan. |
| OCR for one approved scanned report | Yellow | Requires OCR-specific approval and retention policy. |
| Embeddings for approved content | Yellow | Requires explicit embedding approval, retention policy, and no model training. |
| Bulk content extraction | Red | Blocked. |
| Model training on report/client data | Red | Blocked unless separately approved in writing. |
| Cross-firm data mixing | Red | Blocked. |
| Client-visible intelligence | Red | Blocked. |
| Uncontrolled evidence preview | Red | Blocked. |
| Commit real source files or extracted content | Red | Always prohibited. |

## 9. Explicit Blocked Actions

The following remain blocked unless a future approval explicitly changes policy:

- Bulk content extraction.
- Model training, fine-tuning, evaluation datasets, prompt libraries, or vendor improvement using report/client data.
- Cross-firm or cross-tenant data mixing.
- Client-visible Firm Intelligence cards, passport details, evidence summaries, audit metadata, or internal comp/fact recommendations.
- Uncontrolled evidence preview.
- Repository commits containing real reports, source documents, extracted text, OCR output, embeddings, vector stores, exports, PDFs, DOCX, XLSX, CSV, TSV, or TXT files.

## 10. Final Approval Record

Final pilot decision:

- Approved:
- Approved with restrictions:
- Rejected:
- Deferred:

Required signatures:

| Role | Name | Date | Decision | Notes |
| --- | --- | --- | --- | --- |
| Company owner/executive sponsor |  |  |  |  |
| Legal/privacy reviewer |  |  |  |  |
| Appraisal compliance lead |  |  |  |  |
| Security/IT owner |  |  |  |  |
| Product owner |  |  |  |  |
| Engineering owner |  |  |  |  |

The pilot must not begin until all required approvals are complete and the final decision is approved.
