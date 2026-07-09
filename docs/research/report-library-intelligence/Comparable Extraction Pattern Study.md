# Comparable Extraction Pattern Study

Prepared for Falcon Intelligence  
Future system: Property Library / Controlled Comp Vault  
Output folder: AI - Falcon Intelligence Inventory  
Research posture: schema-planning only; no CSV, JSON, or database import files created.

## 1. Research Basis

This pass reviewed likely completed DOCX reports in retail, restaurant, office, industrial/flex, and mixed-use folders where comparable sale or rental grids appeared likely to be present. The work focused on table structure, repeated comparable patterns, and controlled-vault schema design. It did not attempt a database import.

Report categories sampled:

- Retail
- Restaurant
- Office
- Industrial (Flex)
- Mixed Use

Common sample sources included 2024, 2025, and 2026 completed or revised reports. The strongest extraction signals came from DOCX tables, because they expose rows and cells directly. Some comparable sections still require narrative parsing because sale sheets are sometimes split into multiple vertical tables, summary grids, adjustment grids, and comments.

## 2. High-Level Findings

- Comparable data is present in several different layouts, not one consistent grid.
- Rental comps are more often stored in simple horizontal tables than sale comps.
- Sale comps frequently use vertical detail sheets plus separate adjustment grids.
- Some reports include small capitalization-rate summary tables with only location, sale date, sale price, property type, and cap rate.
- The same comparable property can appear across multiple reports with identical data, changed data, abbreviated address, altered use classification, or different lease terms.
- Several fields are clearly appraiser- or report-dependent, especially comments, verification wording, lease type abbreviations, property rights labels, and condition/quality descriptions.
- Auto-import is unsafe without evidence records, source report links, and human approval.

## 3. Common Comparable Sale Table Layouts

### Layout A: Vertical Sale Identification Sheet

Observed pattern:

- Two-column table.
- First column contains labels.
- Second column contains values.
- Usually appears before or beside a larger sale detail table.

Common fields:

- `Address`
- `Parcel #`
- `Sale Price`
- `Sale Date`
- `Conveyance #`
- `Verification`
- `Verification Date`

Example observed structure:

| Field | Value |
| --- | --- |
| Address | Comparable address |
| Parcel # | Parcel identifier |
| Sale Price | Dollar amount |
| Sale Date | Transaction date |
| Conveyance # | Instrument or conveyance number |
| Verification | Public records, CoStar, buyer/seller, broker |
| Verification Date | Month/year and appraiser initials |

Extraction implication:

- This layout is highly importable after field-label normalization.
- It often must be joined to the following sale detail table to form one full comparable record.

### Layout B: Vertical Sale Detail Sheet

Observed pattern:

- Multi-column table, often with labels on the left and additional labels on the right.
- Some cells are blank spacer cells.
- A comments row may span or appear as a long final row.

Common fields:

- `Rights Conveyed`
- `Financing`
- `Conditions of Sale`
- `Grantor`
- `Grantee`
- `Building Size`
- `Construction Quality`
- `Condition`
- `Price / Square Foot`
- `Zoning`
- `Site Size`
- `Land to Bldg. Ratio`
- `Utilities`
- `Location`
- `Interior Finish`
- `Age/Effective Age`
- `Comments`

Extraction implication:

- Requires row-pair parsing rather than simple header-row parsing.
- Some labels appear on the left with their value beside them, while the right side contains another label whose value may be in a later or adjacent cell.
- Comments are valuable but should stay as evidence text until appraiser-approved.

### Layout C: Horizontal Sale Summary Table

Observed pattern:

- Header row across the top.
- Each row is a comparable sale.
- Often used for cap-rate support or a quick sale summary.

Common fields:

- `Location`
- `Sale Date`
- `Sale Price`
- `Property Type`
- `Cap Rate`
- `NOI`

Example observed structures:

| Location | Sale Date | Sale Price | Property Type | Cap Rate |
| --- | --- | --- | --- | --- |
| City, State | Month-year | Dollar amount | Retail / Office / Self-storage | Percent |

| Location | Sale Price | NOI | Cap Rate |
| --- | --- | --- | --- |
| Street address | Dollar amount | Dollar amount | Percent |

Extraction implication:

- These tables usually do not contain enough identity detail to create a canonical property record alone.
- They should create evidence events linked to a possible property identity, then enter the review queue.

### Layout D: Sales Comparison Adjustment Grid

Observed pattern:

- Subject and comparables appear as columns or rows.
- Adjustment factors include transaction and property characteristics.
- Unit values and adjusted values are included.

Common fields:

- Address or sale number
- Sale price
- Sale date
- Price per SF
- Property rights
- Financing
- Conditions of sale
- Market conditions
- Location
- Size
- Age / condition
- Quality
- Land-to-building ratio
- Adjusted unit value

Extraction implication:

- Adjustment grids are analytical evidence, not raw property identity evidence.
- Import should preserve them as report-usage evidence and adjustment-event data, not overwrite base comp facts automatically.

## 4. Common Rental Comparable Table Layouts

### Layout A: Retail Rental Comparable Grid

Observed pattern:

- Horizontal table.
- One row per rental comp.
- Often used in retail and restaurant reports.

Common fields:

- `Property`
- `Size`
- `Rental Rate`
- `Terms`
- `Comments`

Example observed structure:

| Property | Size | Rental Rate | Terms | Comments |
| --- | --- | --- | --- | --- |
| Street address, city, county, state | Suite or size range | Dollar/SF or range | NNN / MG | Building and location notes |

Extraction implication:

- Good first candidate for automated extraction.
- Needs cleanup for OCR-like spacing artifacts in DOCX text, such as `S ize`, extra spaces in dollar amounts, and inconsistent `/SF` formatting.

### Layout B: Subject Rent Roll / Lease Summary

Observed pattern:

- Horizontal table.
- Rows are subject tenants, not market comps.
- Appears near income approach sections.

Common fields:

- `Tenant`
- `Suite Size`
- `Annual Rent`
- `Rent/SF Terms`
- `Exp. Date`
- `Term Length`

Extraction implication:

- Must not be imported as external rent comparables.
- Should be classified as subject lease evidence, not comp-vault evidence.

### Layout C: Industrial Rental Comparable Grid

Observed pattern:

- Horizontal table.
- One row per industrial rent comp.

Common fields:

- `Property`
- `Use`
- `Rental Rate / SF`
- `Lease Terms`
- `Tenant Size`
- `Vacancy`

Example observed structure:

| Property | Use | Rental Rate / SF | Lease Terms | Tenant Size | Vacancy |
| --- | --- | --- | --- | --- | --- |
| Rental One: address | Industrial | Dollar/SF | NNN | SF | Percent |

Extraction implication:

- Highly extractable with property-type-specific normalization.
- `Property` often includes sequence labels like `Rental One:` that must be stripped from the canonical address.

### Layout D: Mixed-Use Residential Rental Grid

Observed pattern:

- Horizontal table.
- Includes apartment unit type and monthly rent rather than commercial rent/SF.

Common fields:

- `Address`
- `Type`
- `Rent/Month`
- `Vacancy`

Extraction implication:

- Should not be normalized into the commercial rent comp schema without a subtype flag.
- Should route to a residential-unit rental schema or remain report evidence only until Falcon supports that subtype.

### Layout E: Mixed-Use Commercial Rent Grid

Observed pattern:

- Horizontal table.
- Similar to retail grid but often includes building age and occupancy comments.

Common fields:

- `Property`
- `Rent/SF`
- `Lease Terms`
- `Suite Size`
- `Building Age`
- `Comments`

Extraction implication:

- Good candidate for import after type classification.
- Building age may be a property attribute, a lease evidence attribute, or both depending on source reliability.

## 5. Common Fields That Appear Consistently

### Sale Comps

Most consistent sale comp fields:

- Address or location
- Sale date
- Sale price
- Property type
- Building size
- Site size
- Price per SF
- Grantor
- Grantee
- Financing
- Conditions of sale
- Property rights conveyed / rights conveyed
- Verification source
- Verification date
- Zoning
- Condition
- Construction quality
- Comments

### Rental Comps

Most consistent rent comp fields:

- Property or address
- Use
- Suite size / tenant size
- Rental rate / SF
- Lease terms
- Vacancy
- Comments
- Tenant, when subject lease or rent roll
- Annual rent, when subject lease or income approach
- Lease expiration or term length, when subject lease

### Identity Fields

Fields most useful for recognizing the same property:

- Street address
- City
- County
- State
- Parcel number
- Building size
- Site size
- Property type
- Year built or building age
- Zoning

## 6. Missing, Inconsistent, Renamed, or Author-Dependent Fields

### Label Variants

- `Sale Price`, `Sales Price`, `Sales Price per SF`, `Sale Price / SF`, `Price / Square Foot`
- `Property Rights Conveyed`, `Rights Conveyed`, `Property Rights`
- `Conditions of Sale`, `Condition of Sale`, `Conditions`
- `Financing`, `Terms`, `Cash Equivalent`
- `Building Size`, `Building Area`, `GBA`, `Gross Building Area`
- `Site Size`, `Land Area`, `Acreage`
- `Rental Rate`, `Rental Rate / SF`, `Rent/SF`, `Rent /SF Terms`, `Lease Rate`
- `Lease Terms`, `Terms`, `Expense Structure`, `NNN`, `MG`, `Modified Gross`
- `Tenant Size`, `Suite Size`, `Space Size`, `Size`
- `Vacancy`, `Occupancy`, `Percent Occupied`

### Missing or Weak Fields

- Full address may be reduced to city/state in cap-rate summary tables.
- County is often present in rental retail grids but absent in sale summaries.
- Parcel number is common in detailed sale sheets but missing from rent comps.
- Verification source is common in sale sheets but uncommon in rent grids.
- Verification date may include appraiser initials in the same cell.
- Building size and site size may be missing from summary tables.
- Lease date is often missing in rental comp tables.
- Tenant name is often absent for external rental comps.
- Cap rate support tables may omit NOI source and occupancy assumptions.
- Comments vary significantly in detail and reliability.

### Author-Dependent or Report-Dependent Fields

- Appraiser initials appended to verification date.
- First-person versus team verification language.
- Abbreviations such as `MG`, `Mod. Gross`, `Modified Gross`, `N NN`, and `NNN`.
- Comments may mention broker exposure, listing period, occupancy, renovation, or source caveats inconsistently.
- Some rows include `Rental One:` or `Comparable Sale #1` as part of the property cell.
- Some values have extra internal spacing from Word layout artifacts, such as `$ 1 5 . 64` or `1, 9 00 SF`.

## 7. Same Comparable Across Multiple Reports

Repeated comparable usage was observed. Some examples are exact reuse; others show likely same property with changed or context-specific fields.

### Reused Retail Rent Comps

The following rental comps appeared in both a 2024 Tiffin retail report and a 2025 Findlay retail report with effectively matching fields:

- `716 W. Market Street, Tiffin, Seneca County, Ohio`
- `2028 Tiffin Avenue, Findlay, Hancock County, Ohio`
- `2020 Tiffin Avenue, Findlay, Hancock County, Ohio`
- `1044-1306 Oak Harbor Road, Fremont, Sandusky County, Ohio`

Observed repeated values:

- `716 W. Market Street`: `1,000 to 1,375 SF`, `$10-$12/SF`, `NNN`, comment about a 6,800 SF multi-tenant building near Kroger.
- `2028 Tiffin Avenue`: `2,500 SF`, `$11.04/SF`, `MG`, comment about retail suite in a 10,000 SF multi-tenant building.
- `2020 Tiffin Avenue`: `3,750 SF`, `$10.00/SF`, `NNN`, retail/storage space in an 18,000 SF multi-tenant building.
- `1044-1306 Oak Harbor Road`: `1,888 to 3,610 SF`, `$7.00`, `NNN`, space in a large multi-tenant retail building.

Interpretation:

- These are strong candidates for controlled comp vault records.
- They should still import first as evidence events because the same repeated row may have originated from an older report rather than a freshly verified source.

### Same Address With Conflicting or Context-Specific Rent Data

`2028 Tiffin Avenue, Findlay` appeared in multiple reports with different rent evidence:

- Retail report use: `2,500 SF`, `$11.04/SF`, `MG`, retail suite in a 10,000 SF multi-tenant building.
- Office report use: `Rental Five: 2028 Tiffin Avenue, Findlay`, `$12.00`, `NNN`, `2,500 SF`, `Office /Retail`.

Interpretation:

- This may represent updated information, a different suite, different lease terms, a changed source, or a report-specific judgment.
- The property identity may match, but the rent event should not overwrite the prior rent event.

### Mixed-Use Reuse Examples

`207-209 Louisiana Avenue, Perrysburg` appeared as a residential rental comparable in more than one mixed-use report:

- `3 Bedroom`, `$1,500`, `0% vacancy`

Interpretation:

- This should be classified as residential rental evidence, not commercial rent/SF evidence.

`120-122 Louisiana Avenue, Perrysburg`, `140 N Main St, Bowling Green`, and `522 E Wooster St, Bowling Green` appeared in more than one mixed-use report in capitalization or rate-support contexts.

Interpretation:

- These may be property identities reused across income support tables, but a low-column table with only an address and rate is too thin for automated canonical import.

## 8. Examples of Conflicting Data for Same Property

These examples should become test cases for the review queue rather than auto-merge cases.

### `2028 Tiffin Avenue, Findlay`

Observed differences:

- Rent rate: `$11.04/SF` versus `$12.00/SF`
- Lease terms: `MG` versus `NNN`
- Use: retail suite versus `Office /Retail`
- Address formatting: full county/state format versus shortened city format

Recommended treatment:

- Same candidate property identity.
- Separate rent evidence events.
- Human review required before choosing any current normalized market rent.

### `1044-1306 Oak Harbor Road, Fremont`

Observed issue:

- Multi-address or range address.
- Rent row describes spaces from `1,888 to 3,610 SF`.
- Rental rate shown as `$7.00` without explicit `/SF` in one table.

Recommended treatment:

- Normalize as a property range address.
- Keep suite-size range as an event-level field.
- Infer `/SF` only with review, not automatically.

### `716 W. Market Street, Tiffin`

Observed issue:

- Rent shown as `$10-$12/SF`.
- Size shown as `1,000 to 1,375 SF`.
- Same data repeats across reports.

Recommended treatment:

- Store min/max rent and min/max suite size.
- Do not collapse to an average unless a derived field is explicitly approved.

### `207-209 Louisiana Avenue, Perrysburg`

Observed issue:

- Address range.
- Residential unit type, not commercial suite.
- Monthly rent rather than annual or per-square-foot rent.

Recommended treatment:

- Route to residential rent subtype or evidence-only queue.
- Do not coerce into commercial rent comp schema.

## 9. Proposed Property Identity Schema

Purpose: identify a real property independent of any single sale, lease, or report usage.

Recommended fields:

- `property.id`
- `property.identity_status`
- `property.primary_address`
- `property.normalized_address`
- `property.address_range`
- `property.unit_or_suite`
- `property.city`
- `property.county`
- `property.state`
- `property.zip`
- `property.parcel_numbers[]`
- `property.latitude`
- `property.longitude`
- `property.property_type_primary`
- `property.property_type_secondary`
- `property.building_size_sf`
- `property.site_size_acres`
- `property.site_size_sf`
- `property.year_built`
- `property.zoning_code`
- `property.zoning_jurisdiction`
- `property.source_confidence`
- `property.identity_notes`
- `property.created_from_report_id`
- `property.last_reviewed_by`
- `property.last_reviewed_date`

Identity status values:

- `unreviewed_candidate`
- `appraiser_confirmed`
- `needs_research`
- `duplicate_candidate`
- `merged`
- `do_not_import`

## 10. Proposed Sale Comp Schema

Purpose: store a transaction event involving a property.

Recommended fields:

- `sale.id`
- `property.id`
- `sale.event_status`
- `sale.sale_date`
- `sale.sale_price`
- `sale.sale_price_normalized`
- `sale.price_per_sf`
- `sale.price_per_unit`
- `sale.property_rights_conveyed`
- `sale.financing`
- `sale.conditions_of_sale`
- `sale.grantor`
- `sale.grantee`
- `sale.instrument_number`
- `sale.conveyance_number`
- `sale.verification_source`
- `sale.verification_contact`
- `sale.verification_date`
- `sale.verified_by`
- `sale.source_report_id`
- `sale.source_report_section`
- `sale.source_table_type`
- `sale.raw_address_text`
- `sale.raw_row_text`
- `sale.comments`
- `sale.import_confidence`
- `sale.review_required`
- `sale.review_reason`

Suggested normalized enums:

- `sale.property_rights_conveyed`: `fee_simple`, `leased_fee`, `leasehold`, `unknown`
- `sale.financing`: `cash_equivalent`, `seller_financing`, `conventional`, `unknown`
- `sale.conditions_of_sale`: `arms_length`, `distress`, `related_party`, `portfolio`, `unknown`
- `sale.event_status`: `unreviewed`, `approved`, `rejected`, `superseded`, `merged`

## 11. Proposed Rent Comp Schema

Purpose: store lease or market rent evidence associated with a property.

Recommended fields:

- `rent.id`
- `property.id`
- `rent.event_status`
- `rent.rent_type`
- `rent.tenant_name`
- `rent.use`
- `rent.suite_or_unit`
- `rent.suite_size_sf`
- `rent.suite_size_min_sf`
- `rent.suite_size_max_sf`
- `rent.rent_rate_psf`
- `rent.rent_rate_min_psf`
- `rent.rent_rate_max_psf`
- `rent.rent_per_month`
- `rent.annual_rent`
- `rent.lease_terms`
- `rent.expense_structure`
- `rent.lease_date`
- `rent.expiration_date`
- `rent.term_months`
- `rent.vacancy_percent`
- `rent.occupancy_percent`
- `rent.source_type`
- `rent.verification_source`
- `rent.verification_date`
- `rent.source_report_id`
- `rent.source_report_section`
- `rent.source_table_type`
- `rent.raw_property_text`
- `rent.raw_row_text`
- `rent.comments`
- `rent.import_confidence`
- `rent.review_required`
- `rent.review_reason`

Suggested `rent.rent_type` values:

- `commercial_market_rent`
- `subject_lease`
- `asking_rent`
- `residential_unit_rent`
- `ground_rent`
- `unknown`

Suggested `rent.expense_structure` values:

- `nnn`
- `modified_gross`
- `gross`
- `full_service`
- `unknown`

## 12. Proposed Evidence Event Schema

Purpose: preserve source-specific facts before they are approved into canonical property, sale, or rent records.

Recommended fields:

- `evidence.id`
- `evidence.event_type`
- `evidence.extracted_entity_type`
- `evidence.source_report_id`
- `evidence.source_report_path`
- `evidence.source_report_date`
- `evidence.source_property_type`
- `evidence.source_section`
- `evidence.source_table_index`
- `evidence.source_row_index`
- `evidence.source_column_index`
- `evidence.raw_text`
- `evidence.raw_cells_json`
- `evidence.normalized_candidate_json`
- `evidence.extraction_method`
- `evidence.extraction_confidence`
- `evidence.match_candidate_property_ids[]`
- `evidence.match_confidence`
- `evidence.conflict_flags[]`
- `evidence.review_status`
- `evidence.reviewed_by`
- `evidence.reviewed_date`
- `evidence.review_notes`

Recommended event types:

- `sale_identity_sheet`
- `sale_detail_sheet`
- `sale_summary_row`
- `sale_adjustment_grid`
- `rent_comp_row`
- `subject_rent_roll_row`
- `cap_rate_summary_row`
- `narrative_comp_reference`

## 13. Proposed Report Usage Schema

Purpose: record how a property, sale, or rental event was used in a specific appraisal report.

Recommended fields:

- `usage.id`
- `report.id`
- `report.path`
- `report.year`
- `report.property_type`
- `report.subject_address`
- `report.appraiser`
- `comp.property_id`
- `comp.sale_id`
- `comp.rent_id`
- `usage.comp_role`
- `usage.comp_number`
- `usage.approach`
- `usage.section`
- `usage.grid_type`
- `usage.unit_of_comparison`
- `usage.unadjusted_value`
- `usage.adjusted_value`
- `usage.adjustment_summary`
- `usage.weighting_notes`
- `usage.raw_label`
- `usage.raw_row_text`
- `usage.created_from_evidence_id`

Suggested `usage.comp_role` values:

- `sale_comparable`
- `rent_comparable`
- `cap_rate_comparable`
- `land_sale_comparable`
- `subject_lease`
- `excluded_or_discussed`

## 14. Normalization Rules

### Address Normalization

- Remove comp sequence prefixes such as `Rental One:`, `Rental Two:`, `Comparable Sale #1`, and `Sale 1`.
- Normalize street suffixes: `Street/St.`, `Avenue/Ave.`, `Road/Rd.`, `Boulevard/Blvd.`, `Drive/Dr.`, `Parkway/Pkwy`.
- Preserve address ranges such as `1044-1306 Oak Harbor Road` and `207-209 Louisiana Avenue`.
- Preserve suite/unit identifiers separately from street address when visible.
- Normalize city/state spelling and casing.
- Do not discard county text; store county as a separate field when present.
- Keep the original raw address string in every evidence event.

### Numeric Normalization

- Remove internal spacing in numbers and currency, such as `$ 1 5 . 64`.
- Convert `1, 9 00 SF` to `1900`.
- Store displayed ranges as min/max fields, not averages.
- Normalize percentages to decimal or percent consistently, but keep the raw string.
- Parse `per SF`, `/SF`, `SF`, `PSF`, and `Price / Square Foot` into standard unit fields.
- Do not infer missing `/SF` unless table context is strong and the row is flagged for review.

### Date Normalization

- Convert month-year values such as `May-25` to a normalized partial date with precision flag.
- Preserve exact dates when available.
- Split verification date from appraiser initials when present.
- Store date precision: `day`, `month`, `year`, or `unknown`.

### Lease Term Normalization

- Normalize `NNN`, `N NN`, `triple net` to `nnn`.
- Normalize `MG`, `Mod. Gross`, `Modified Gross` to `modified_gross`.
- Keep ambiguous terms as `unknown` with raw text preserved.

### Property Type Normalization

- Map report labels to controlled categories: `retail`, `restaurant`, `office`, `industrial`, `flex`, `mixed_use`, `self_storage`, `residential_unit`, `land`, `special_use`.
- Allow multiple classifications because some comps are `Office /Retail` or `Retail/Office`.
- Do not overwrite canonical property type from one report if another report uses a different type; store type observations as evidence.

### Verification Normalization

- Split verification source into source types when possible: `public_records`, `auditor`, `assessor`, `costar`, `loopnet`, `buyer`, `seller`, `broker`, `appraiser_file`.
- Preserve source phrase exactly.
- Store verifier initials separately only when confidently parsed.

## 15. Candidate Matching Rules

### Strong Match

Candidate is a strong property identity match when:

- Normalized street address, city, and state match exactly; or
- Parcel number matches exactly; or
- Geocoded coordinates match and address similarity is high.

Action:

- Link evidence event to existing property candidate.
- Still require review if sale/rent values conflict with approved facts.

### Probable Match

Candidate is a probable match when:

- Street number and street name match, but city/county/state is abbreviated or missing.
- Address range overlaps, such as `120 & 122 Louisiana` versus `120-122 Louisiana`.
- Street suffix differs but city/state match.
- Building size and property type are similar.

Action:

- Queue for human review before merge.

### Weak Match

Candidate is a weak match when:

- Only city/state and property type match.
- Only a partial street name is present.
- Summary table provides location but no address.
- Address appears in comments but not structured cells.

Action:

- Do not merge.
- Store as evidence-only until researched.

### Duplicate Event Match

Sale or rent event is likely duplicate evidence when:

- Same property identity.
- Same sale date and sale price.
- Same grantor/grantee or same verification source.
- Same rent rate, suite size, lease terms, and comment text.

Action:

- Link as repeated report usage of the same evidence event, not a new canonical event.
- Preserve each report usage record.

### Conflict Match

Conflict exists when same candidate property has:

- Different sale price for same sale date.
- Different sale date for same grantor/grantee.
- Different rent rate for same suite size and lease terms.
- Different lease terms for same apparent rental comp.
- Different building size or site size beyond tolerance.
- Different property type across reports.

Action:

- Do not overwrite.
- Create review queue item.
- Require appraiser approval or source research.

## 16. Recommended Duplicate-Detection Rules

### Property Duplicate Rules

- Exact normalized address + city + state match.
- Parcel number match.
- Address range overlap + same city + same property type.
- High fuzzy address score + same county + similar building size.

### Sale Event Duplicate Rules

- Same property + same sale date + same sale price.
- Same property + same conveyance/instrument number.
- Same grantor + grantee + sale price, even if address formatting differs.

### Rent Event Duplicate Rules

- Same property + same suite size + same rent rate + same lease terms.
- Same property + same tenant + same annual rent.
- Same property + same row comment text across reports.

### Report Usage Duplicate Rules

- Same report path + same section + same comp number.
- Same report path + same raw row text.

## 17. Human Review Workflow

### Intake

1. Extract evidence rows from completed reports.
2. Classify each row as sale comp, rent comp, subject lease, cap-rate support, adjustment grid, or non-comp table.
3. Normalize obvious formatting while preserving raw text.
4. Generate candidate property matches.
5. Assign confidence and conflict flags.

### Review Queue Fields

Recommended queue fields:

- `review.item_id`
- `review.priority`
- `review.status`
- `review.source_report_path`
- `review.source_report_subject`
- `review.source_report_date`
- `review.comp_type`
- `review.raw_property_text`
- `review.normalized_property_candidate`
- `review.match_candidates`
- `review.extracted_sale_fields`
- `review.extracted_rent_fields`
- `review.conflict_summary`
- `review.missing_required_fields`
- `review.recommended_action`
- `review.appraiser_decision`
- `review.approved_property_id`
- `review.approved_sale_id`
- `review.approved_rent_id`
- `review.reject_reason`
- `review.notes`
- `review.reviewed_by`
- `review.reviewed_date`

### Appraiser Decision Options

- Approve new property.
- Link to existing property.
- Approve new sale event.
- Link to existing sale event.
- Approve new rent event.
- Link to existing rent event.
- Mark as subject lease only.
- Mark as evidence only.
- Reject as non-comparable.
- Needs source research.

### Required Human Review Triggers

- Address range.
- Missing city or state.
- Only city/state location available.
- Rent range or size range.
- Conflicting rent rate or lease terms.
- Conflicting building size or site size.
- Property type differs across reports.
- Sale price lacks date.
- Verification source missing.
- Cap-rate table without property-level detail.
- Mixed-use or residential-unit rent evidence.
- Any field inferred from context rather than directly extracted.

## 18. Risks That Make Auto-Import Unsafe

- Same address can represent different suites, tenants, or lease events.
- Same property can be used as retail in one report and office/retail in another.
- Rent rate and lease terms can conflict across reports.
- Some values are ranges, not point estimates.
- Some summary tables lack full address, parcel, size, or verification.
- Subject rent rolls can look like rent comp grids but should not enter the external comp vault.
- Adjustment grids contain appraiser analysis, not raw market facts.
- Reused comparable rows may be stale and not newly verified.
- Word extraction introduces spacing artifacts that can corrupt numbers.
- Verification dates can include appraiser initials.
- Cap-rate tables may include derived data without enough source detail.
- Address ranges and multi-building properties require identity decisions.
- Duplicate revised/final reports can create repeated evidence if report lineage is not controlled.
- Full legal reliability requires source traceability back to the report and, ideally, supporting workfile documents.

## 19. Recommended First Gold-Set Reports for Testing Extraction

The first gold set should include reports with clear, representative sale and rental layouts and known repeated comps.

Recommended initial test reports:

- `2024 Reports\Retail\378-382 W Market Street, Tiffin, OH\Revised 378-382 W. Market Report.docx`
- `2025 Reports\Retail\2716 N Main Street, Findlay, OH\Revised 2716 N. Main Street Report.docx`
- `2025 Reports\Office\621 & 631 Bright Road, Findlay, OH\revised 621-631 Bright Road Report.docx`
- `2025 Reports\Retail\130 S Main Street, Fredericktown, OH\Revised 6-24-2025 Report - 130 S. Main St., Fredericktown, OH.docx`
- `2025 Reports\Industrial (Flex)\400 Van Camp Road, Bowling Green, OH\Final Report - 400 Van Camp Road, Bowling Green OH.docx`
- `2025 Reports\Industrial (Flex)\6660 Fritchie Road, Port Clinton, OH\Final Report -6660 Fritchie Road, Port Clinton OH.docx`
- `2025 Reports\Industrial (Flex)\205 W Railroad Street, Bloomdale, OH\Revised 6-24-2025 - Report - 205 W. Railroad St., Bloomdale, OH.docx`
- `2025 Reports\Mixed Use\117 Louisiana Avenue, Perrysburg, OH\Revised 117 Lousiana Avenue Report.docx`
- `2024 Reports\Mixed Use\318-320 Conant Street, Maumee, OH\318-320 Conant St, Maumee REVISED.docx`
- `2024 Reports\Mixed Use\128 S Prospect Avenue, Bowling Green OH\Revised Report - 128 S Prospect Street, Bowling Green OH.docx`
- `2025 Reports\Office\300 Clinton Street, Defiance, OH\Revised 300 S. Clinton Street.docx`
- `2025 Reports\Office\6048 Deer Park Ct, Toledo, OH\6048 Deer Park old report.docx`

Why these are useful:

- They include repeated retail rent comps.
- They include a same-address conflict case.
- They include subject rent roll tables that must not be imported as external comps.
- They include industrial rental grids.
- They include mixed-use residential rent evidence.
- They include sale-cap-rate summary tables.
- They include vertical sale detail sheets.

## 20. Recommended Controlled Comp Vault Build Sequence

1. Build report selector and deduplication logic for final/revised/complete versions.
2. Build DOCX table extractor with table classification.
3. Build field-label normalization dictionary.
4. Build address and numeric cleanup functions.
5. Store every extracted row first as an evidence event.
6. Add property identity candidate matching.
7. Add duplicate event detection.
8. Add conflict detection.
9. Build appraiser review queue.
10. Approve a small retail/office/industrial gold set manually.
11. Only after gold-set review, design CSV/JSON import output.

## 21. Immediate Recommendations

- Treat the Controlled Comp Vault as evidence-first, not import-first.
- Separate `property identity`, `sale event`, `rent event`, and `report usage`.
- Never let one report overwrite another report's comp facts automatically.
- Require appraiser approval for conflicts, inferred units, address ranges, and same-address rent differences.
- Start with rental comp grids because they are more consistently tabular.
- Treat sale comp vertical sheets as phase two because they require joining multiple adjacent tables.
- Keep raw row/cell text permanently for auditability.
