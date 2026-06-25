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
