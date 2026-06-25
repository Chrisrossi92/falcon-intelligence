# Property Library and Controlled Comp Vault

The Property Library is the synthetic foundation for appraisal property intelligence and controlled comparable evidence. It is a searchable workspace preview only. It does not ingest real reports, OCR source files, create embeddings, connect to OneDrive, or read completed report files.

## Purpose

The workspace separates four concepts that should not be collapsed:

- Property identity: the canonical property record.
- Evidence events: sale, lease, expense, cap-rate, tax, and subject-assignment events tied to a property.
- Report usages: how a property was used in a specific synthetic report/order.
- Candidate normalization: possible duplicate or conflicting records requiring review before merge.

This keeps property identity stable while allowing evidence and report usage history to grow over time.

## Property Record

Each synthetic property record includes:

- Canonical property identity.
- Address, city, county, and state.
- Property type and subtype.
- Synthetic latitude and longitude.
- Building size, site size, year built, condition, and zoning.
- Verification status.

Verification status describes the canonical record only. Individual evidence events can have separate verification states.

## Evidence Events

A property can have many evidence events:

| Event Type | Meaning |
| --- | --- |
| `sale` | Sale price or price-derived market evidence. |
| `lease_rent` | Rent, renewal, or lease support. |
| `expense` | Operating expense support. |
| `cap_rate` | Capitalization-rate support. |
| `assessment_tax` | Assessment or tax support. |
| `subject_assignment` | The property was a subject in an assignment. |

Evidence events are source-labeled synthetic records. They are not extracted from source documents.

## Report Usages

Report usages track how a property appears in a synthetic report/order:

- `subject_property`
- `sale_comparable`
- `rental_comparable`
- `expense_comparable`
- `cap_rate_support`
- `narrative_reference`

This lets the same property be a subject in one assignment and a comparable or support item in another without duplicating the property identity.

## Candidate Normalization

Candidate matches show where duplicate or conflicting records may need future merge review.

The synthetic model supports:

- Same address with conflicting size.
- Same sale with different price or price/SF.
- Same comp used by different appraisers.
- Confidence score.
- Review status: `candidate`, `needs_review`, `approved`, `rejected`, or `merged`.

Candidate matches do not merge data automatically. They are review prompts.

## Evidence Corrections and Audit Trail

Property Library fields and comparable candidate fields can be corrected through the synthetic Evidence Correction and Audit Trail model.

The correction model records:

- Prior value and corrected value.
- Original actor and correcting actor.
- Timestamp, reason, and review status.
- Supporting synthetic evidence reference.
- Confidence impact before and after correction.
- Append-only audit events.

Approved corrections resolve the current trusted value. Proposed, needs-review, and rejected corrections remain visible in history but do not silently overwrite the trusted value.

Example demo scenario:

- Chad originally entered a comparable GBA of `4,200 SF`.
- Chris corrected the GBA to `4,800 SF`.
- The reason is `based on auditor`.
- The support is a synthetic auditor property record card.
- Confidence increases from `58` to `88`.

Preview the JSON model:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli correction-audit
```

The React workspace preview also surfaces this correction in the Passport drawer as a compact Field History panel. The panel shows Correction, Prior Value, Current Value, Supporting Evidence, Confidence before/after, approval status, and the synthetic audit event history. It remains read-only and does not persist user edits.

## Workspace Preview

The CLI returns a JSON view model shaped like a future appraiser-facing workspace:

- Map placeholder with synthetic markers.
- Filter controls and available filter values.
- Results table.
- Selected property drawer.
- Candidate normalization conflicts.

Preview all synthetic properties:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli property-library
```

Filter the workspace:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli property-library --property-type Commercial --county "Montgomery County" --comp-role sale_comparable
```

Open a synthetic details drawer:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli property-library --selected-property-id prop-riverview-517
```

## Guardrails

- Use synthetic/demo values only.
- Do not ingest completed reports, source documents, OCR output, embeddings, or OneDrive data.
- Do not treat candidate matches as merged records.
- Do not promote evidence to a controlled comp vault without a future verification workflow.
- Do not generate report language or Word output from this workspace.

See `docs/appraisal-intelligence-data-model.md` for future verified intelligence entities.
See `docs/data-confidence-provenance-model.md` for future data passport and evidence-link rules.
See `docs/report-field-registry.md` for the Subject Profile control layer.
