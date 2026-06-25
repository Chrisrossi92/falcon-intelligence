# Report Field Registry

The Report Field Registry is the first structured control layer for future report assembly. It is not a report generator and does not read, parse, OCR, embed, export, or merge source documents.

This slice uses synthetic demo data for `517 E Riverview Avenue` only.

## Purpose

The registry gives Falcon Intelligence a stable place to track appraiser-reviewed subject facts before any narrative or Word report workflow exists.

It supports:

- Dot-notation field keys such as `subject.address`, `assignment.intended_use`, and `zoning.code`.
- Field-level status, confidence, source, notes, and report usage counts.
- Appraiser review actions for approving and locking fields.
- Readiness scoring for future report merge eligibility.
- A grouped Subject Profile preview for appraiser-facing review.

## Field Model

Each field includes:

| Field | Purpose |
| --- | --- |
| `key` | Dot-notation registry key. |
| `label` | Human-readable appraiser-facing label. |
| `value` | Synthetic or future verified structured value. |
| `source` | Human-readable provenance label. Current values are synthetic. |
| `confidence` | Integer from 0 to 100 used for review priority. |
| `status` | One of `missing`, `needs_review`, `approved`, or `locked`. |
| `notes` | Appraiser/reviewer context. |
| `usedInReportCount` | Number of future report locations expected to consume the field. |

## Status Semantics

| Status | Meaning |
| --- | --- |
| `missing` | No value is present. The field cannot be approved or locked. |
| `needs_review` | A value exists, but appraiser verification is still required. |
| `approved` | An appraiser has accepted the value for structured workflow use. |
| `locked` | The value is approved and should not change without a future audit event. |

Approved and locked fields are treated as report-merge-ready. Missing and needs-review fields block or reduce readiness.

## Subject Profile Groups

The first profile preview is grouped for appraiser review:

- Assignment Summary
- Current Ownership / Transaction
- Property Identification
- Site Data
- Improvement Data
- Zoning
- Assessment / Tax Data
- Inspection / Photo Observations
- Open Verification Items
- Narrative Themes

These groups are a UI view model over the field registry. They do not imply source-document extraction.

## Readiness Metrics

The profile reports:

- Completion percentage: fields that are not missing.
- Approved or locked percentage: fields accepted by the review workflow.
- Report Merge Readiness percentage: report-used fields that are approved or locked.
- Report Merge Readiness label: `blocked`, `partial`, `nearly_ready`, or `ready`.

This readiness model is intentionally conservative. A profile can be mostly complete but still blocked from report merge if high-impact report fields remain missing or need review.

## CLI Preview

Preview the synthetic profile:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli subject-profile
```

Simulate appraiser actions:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli subject-profile --approve assignment.property_rights --lock transaction.purchase_price
```

The command returns JSON for a future local UI. It does not save local profile data and does not generate a Word report.

## Guardrails

- Use synthetic/demo values only.
- Do not connect this registry to OneDrive or real source documents yet.
- Do not add OCR, embeddings, extraction, or report export from this layer.
- Treat sources as provenance labels until a future approved evidence-link workflow exists.
- Treat narrative themes as structured control notes, not client-ready report language.

See `docs/data-confidence-provenance-model.md` for future evidence and data passport rules.
See `docs/verified-intelligence-workflow.md` for future human verification workflow rules.
