# Report Library Intelligence Inventory

Prepared for Falcon Intelligence  
Research location: appraisal reports library  
Output folder: AI - Falcon Intelligence Inventory  
Research posture: read-only intelligence inventory; no appraisal report files edited, moved, renamed, or deleted.

## 1. Research Basis

This inventory was built from a scan of completed report candidates across the 2023, 2024, 2025, and 2026 report folders, with emphasis on source DOCX files because they preserve headings, section order, metadata, and narrative text more reliably than flattened PDFs. The extraction pass sampled 90 likely completed DOCX reports across commercial categories, then reviewed a targeted retail/restaurant subset for the first commercial retail template recommendation.

The library contains many supporting workfile documents in the same client folders, including invoices, engagement letters, maps, plats, photos, leases, zoning excerpts, market reports, auditor cards, and comparable data sheets. Those were treated as supporting materials, not completed appraisal reports, unless their filename and folder context suggested a finished report.

Primary completed report filename patterns observed:

- `Complete Report.pdf`
- `Complete Restricted Report.pdf`
- `Report Only.pdf`
- `Report - [address].docx`
- `[address] Report.docx`
- `Final Report - [address].docx`
- `Revised [address] Report.docx`
- `REVISED.docx` variants

## 2. Common Master Report Structure

The dominant structure is highly standardized. Most completed commercial reports follow this order:

1. Cover / title page
2. Appraiser credentials or certification identifiers
3. Table of contents
4. Part I. Introduction
5. Summary of Salient Facts / USPAP Compliancy
6. Scope of Work
7. Part II. Factual Descriptions
8. Area Data
9. Neighborhood Description
10. Market Trend Analysis
11. Zoning
12. Tax and Assessment Data
13. Site Description
14. Building Improvement Detail
15. Part III. Analysis and Conclusions
16. Highest and Best Use Analysis
17. Cost Approach, often not developed
18. Sales Comparison Approach
19. Income Approach - Direct Capitalization, sometimes not developed
20. Reconciliation and Final Value Estimate
21. Final Statement of Value
22. Assumptions and Limiting Conditions
23. Certification
24. Part IV. Appendix

Common deviations:

- Land reports reduce or remove building improvement detail and emphasize land sales.
- Restricted reports compress some narrative and appendices.
- Owner-occupied special-use reports often omit income approach or state that the income approach is not necessary.
- Income-producing retail and multi-tenant reports include stronger income approach support, comparable rental charts, and direct capitalization detail.
- Older PDF-only reports and reports from legacy folders may have similar content but less consistent heading capitalization and filename conventions.

## 3. Common Report Sections and Order

### Part I. Introduction

Typical contents:

- Summary of Salient Facts / USPAP Compliancy
- Type of property
- Property address and legal/geographic identification
- Owner, client, intended user, intended use
- Property rights appraised
- Date of value, date of report, inspection date
- Value conclusion by approach
- Final value conclusion
- Scope of work

### Part II. Factual Descriptions

Typical contents:

- Area Data
- Neighborhood Description
- Market Trend Analysis
- Zoning
- Tax and Assessment Data
- Site Description
- Building Improvement Detail

Retail-specific factual sections usually include visibility, frontage, access, traffic artery context, retail corridor discussion, surrounding commercial uses, parking, site density, condition, tenant/owner occupancy, and building utility.

### Part III. Analysis and Conclusions

Typical contents:

- Highest and Best Use Analysis
- Cost Approach
- Sales Comparison Approach
- Income Approach - Direct Capitalization
- Reconciliation and Final Value Estimate
- Final Statement of Value

Approach treatment varies by property type. Cost approach is frequently included as a section but not developed. Income approach is frequently included as a section but may be not developed for owner-occupied or special-use properties. Sales comparison is the most consistently developed approach.

### Part IV. Appendix

Typical contents:

- Subject photos
- Area map
- Neighborhood map
- Zoning map and code
- Flood map
- Plat map
- Property record card / auditor data
- Comparable sales map
- Comparable rental map, when income approach is developed
- Supporting market or transaction documents, as needed

## 4. Proposed Master Field Registry

The following registry is intended as a first-pass template vocabulary for Falcon Intelligence. Dot notation is grouped by domain so future extraction can map source report text to reusable template fields.

### Assignment

- `assignment.report_type`
- `assignment.report_format`
- `assignment.client`
- `assignment.intended_user`
- `assignment.intended_use`
- `assignment.purpose`
- `assignment.value_premise`
- `assignment.value_type`
- `assignment.property_rights_appraised`
- `assignment.date_of_value`
- `assignment.date_of_report`
- `assignment.inspection_date`
- `assignment.report_number`
- `assignment.effective_interest`
- `assignment.scope_summary`
- `assignment.data_sources`
- `assignment.inspected_by`
- `assignment.inspection_extent`
- `assignment.extraordinary_assumptions`
- `assignment.hypothetical_conditions`

### Subject

- `subject.name`
- `subject.address`
- `subject.street_number`
- `subject.street_name`
- `subject.city`
- `subject.county`
- `subject.state`
- `subject.zip`
- `subject.municipality`
- `subject.township`
- `subject.market_area`
- `subject.neighborhood`
- `subject.property_type`
- `subject.property_subtype`
- `subject.current_use`
- `subject.occupancy_status`
- `subject.owner`
- `subject.tenant`
- `subject.parcel_number`
- `subject.legal_description`
- `subject.census_tract`
- `subject.latitude`
- `subject.longitude`

### Transaction

- `transaction.status`
- `transaction.purchase_price`
- `transaction.contract_date`
- `transaction.sale_date`
- `transaction.sale_price`
- `transaction.grantor`
- `transaction.grantee`
- `transaction.financing`
- `transaction.conditions_of_sale`
- `transaction.property_rights_conveyed`
- `transaction.verification_source`
- `transaction.verification_date`
- `transaction.comments`
- `transaction.prior_sale_history`
- `transaction.listing_history`

### Site

- `site.size_acres`
- `site.size_sf`
- `site.shape`
- `site.frontage`
- `site.depth`
- `site.topography`
- `site.access`
- `site.visibility`
- `site.corner_location`
- `site.traffic_count`
- `site.street_improvements`
- `site.utilities`
- `site.parking_count`
- `site.parking_ratio`
- `site.site_density`
- `site.land_to_building_ratio`
- `site.soil_conditions`
- `site.environmental_conditions`
- `site.flood_zone`
- `site.flood_panel`
- `site.flood_panel_date`
- `site.easements`
- `site.restrictions`

### Zoning

- `zoning.code`
- `zoning.name`
- `zoning.jurisdiction`
- `zoning.permitted_use`
- `zoning.current_use_conformance`
- `zoning.legal_nonconforming_status`
- `zoning.minimum_lot_area`
- `zoning.setbacks`
- `zoning.parking_requirement`
- `zoning.height_limit`
- `zoning.source`
- `zoning.map_reference`

### Improvements

- `improvements.building_count`
- `improvements.gba_sf`
- `improvements.nra_sf`
- `improvements.leasable_area_sf`
- `improvements.year_built`
- `improvements.effective_age`
- `improvements.remaining_economic_life`
- `improvements.construction_quality`
- `improvements.condition`
- `improvements.building_design`
- `improvements.stories`
- `improvements.foundation`
- `improvements.frame`
- `improvements.exterior_walls`
- `improvements.roof_structure`
- `improvements.roof_cover`
- `improvements.windows`
- `improvements.flooring`
- `improvements.walls`
- `improvements.ceilings`
- `improvements.lighting`
- `improvements.plumbing`
- `improvements.hvac`
- `improvements.fire_protection`
- `improvements.interior_finish`
- `improvements.site_improvements`
- `improvements.deferred_maintenance`
- `improvements.personal_property_included`

### Taxes and Assessment

- `taxes.parcel_number`
- `taxes.tax_year`
- `taxes.assessment_year`
- `taxes.land_assessment`
- `taxes.improvement_assessment`
- `taxes.total_assessment`
- `taxes.market_value_by_assessor`
- `taxes.annual_tax_amount`
- `taxes.tax_rate`
- `taxes.special_assessments`
- `taxes.exemptions`

### Market

- `market.source`
- `market.report_date`
- `market.property_sector`
- `market.submarket`
- `market.vacancy_rate`
- `market.absorption_sf`
- `market.net_deliveries_sf`
- `market.under_construction_sf`
- `market.average_rent_psf`
- `market.rent_growth`
- `market.sales_volume`
- `market.transaction_count`
- `market.cap_rate_range`
- `market.trend_summary`

### Highest and Best Use

- `hbu.as_vacant.legally_permissible`
- `hbu.as_vacant.physically_possible`
- `hbu.as_vacant.financially_feasible`
- `hbu.as_vacant.maximally_productive`
- `hbu.as_vacant.conclusion`
- `hbu.as_improved.legally_permissible`
- `hbu.as_improved.physically_possible`
- `hbu.as_improved.financially_feasible`
- `hbu.as_improved.maximally_productive`
- `hbu.as_improved.conclusion`

### Valuation

- `valuation.cost_approach.developed`
- `valuation.cost_approach.indication`
- `valuation.cost_approach.reason_not_developed`
- `valuation.sales_comparison.developed`
- `valuation.sales_comparison.indication`
- `valuation.sales_comparison.unit_value`
- `valuation.sales_comparison.unit_type`
- `valuation.income_approach.developed`
- `valuation.income_approach.indication`
- `valuation.income_approach.reason_not_developed`
- `valuation.income_approach.market_rent_psf`
- `valuation.income_approach.vacancy_rate`
- `valuation.income_approach.expense_ratio`
- `valuation.income_approach.noi`
- `valuation.income_approach.cap_rate`
- `valuation.reconciliation.primary_approach`
- `valuation.reconciliation.supporting_approach`
- `valuation.final_value`
- `valuation.final_value_rounded`
- `valuation.exposure_time`
- `valuation.marketing_time`

### Comparable Sale

- `sale_comps[].address`
- `sale_comps[].city`
- `sale_comps[].county`
- `sale_comps[].state`
- `sale_comps[].property_type`
- `sale_comps[].sale_date`
- `sale_comps[].sale_price`
- `sale_comps[].price_per_sf`
- `sale_comps[].price_per_unit`
- `sale_comps[].site_size_acres`
- `sale_comps[].building_size_sf`
- `sale_comps[].year_built`
- `sale_comps[].condition`
- `sale_comps[].zoning`
- `sale_comps[].grantor`
- `sale_comps[].grantee`
- `sale_comps[].financing`
- `sale_comps[].conditions_of_sale`
- `sale_comps[].property_rights_conveyed`
- `sale_comps[].verification_source`
- `sale_comps[].adjustments.property_rights`
- `sale_comps[].adjustments.financing`
- `sale_comps[].adjustments.conditions_of_sale`
- `sale_comps[].adjustments.market_conditions`
- `sale_comps[].adjustments.location`
- `sale_comps[].adjustments.size`
- `sale_comps[].adjustments.age_condition`
- `sale_comps[].adjustments.quality`
- `sale_comps[].adjustments.site_ratio`
- `sale_comps[].adjusted_unit_value`

### Comparable Rent

- `rent_comps[].address`
- `rent_comps[].city`
- `rent_comps[].property_type`
- `rent_comps[].lease_date`
- `rent_comps[].lease_rate_psf`
- `rent_comps[].lease_type`
- `rent_comps[].tenant`
- `rent_comps[].space_size_sf`
- `rent_comps[].term_months`
- `rent_comps[].expense_structure`
- `rent_comps[].condition`
- `rent_comps[].source`
- `rent_comps[].comments`

### Appraiser and Certification

- `appraiser.primary.name`
- `appraiser.primary.license_number`
- `appraiser.primary.license_state`
- `appraiser.primary.role`
- `appraiser.assistant.name`
- `appraiser.inspector.name`
- `appraiser.signature_date`
- `appraiser.firm.name`
- `appraiser.firm.address`
- `appraiser.certification.statements`

## 5. Proposed Narrative Block Registry

### `narrative.executive_summary`

Purpose: summarize assignment, subject, interest appraised, approaches used, and final opinion of value.

Inputs:

- `subject.address`
- `subject.city`
- `subject.county`
- `subject.state`
- `subject.property_type`
- `assignment.value_type`
- `assignment.property_rights_appraised`
- `assignment.date_of_value`
- `valuation.final_value_rounded`
- `valuation.reconciliation.primary_approach`

Template risk: high. Summary text repeats core values and must remain synchronized with approach sections and final statement.

### `narrative.scope_of_work`

Purpose: state inspection, research, data sources, comparable review, USPAP compliance, and approach applicability.

Inputs:

- `assignment.inspected_by`
- `assignment.inspection_extent`
- `assignment.data_sources`
- `valuation.cost_approach.developed`
- `valuation.sales_comparison.developed`
- `valuation.income_approach.developed`
- `valuation.*.reason_not_developed`

Template risk: high. This is variable boilerplate and should be generated from controlled fields, not freeform AI prose.

### `narrative.area_data`

Purpose: describe broader economic and demographic area context.

Inputs:

- `subject.state`
- `subject.county`
- `subject.city`
- `market.source`
- demographic and economic source fields

Template risk: medium. Stable structure but facts change by market.

### `narrative.neighborhood`

Purpose: define neighborhood boundaries, predominant uses, access, nearby anchors, and competitive positioning.

Inputs:

- `subject.neighborhood`
- `subject.market_area`
- `site.access`
- `site.visibility`
- nearby land use observations
- retail corridor notes

Template risk: medium-high. Reports use similar structure but the narrative is subject-specific.

### `narrative.market_conditions`

Purpose: summarize sector and submarket performance, usually from CoStar or similar market reports.

Inputs:

- `market.source`
- `market.report_date`
- `market.submarket`
- `market.vacancy_rate`
- `market.absorption_sf`
- `market.net_deliveries_sf`
- `market.average_rent_psf`
- `market.rent_growth`
- `market.sales_volume`
- `market.transaction_count`
- `market.trend_summary`

Template risk: high. This block appears formulaic but contains time-sensitive figures and source-specific data.

### `narrative.zoning`

Purpose: identify zoning district, jurisdiction, permitted use, and conformance.

Inputs:

- `zoning.code`
- `zoning.name`
- `zoning.jurisdiction`
- `zoning.permitted_use`
- `zoning.current_use_conformance`
- `zoning.legal_nonconforming_status`

Template risk: high. The boilerplate is stable, but incorrect zoning conclusions are material report errors.

### `narrative.site_description`

Purpose: describe land area, shape, frontage, access, topography, utilities, flood zone, restrictions, and site improvements.

Inputs:

- `site.size_acres`
- `site.size_sf`
- `site.shape`
- `site.frontage`
- `site.depth`
- `site.topography`
- `site.access`
- `site.utilities`
- `site.flood_zone`
- `site.restrictions`
- `site.parking_count`

Template risk: high. It is a repeated field-driven narrative and should be built from validated facts.

### `narrative.improvements`

Purpose: describe building type, size, design, condition, construction, mechanical systems, finish, and functional utility.

Inputs:

- `improvements.gba_sf`
- `improvements.year_built`
- `improvements.condition`
- `improvements.building_design`
- `improvements.foundation`
- `improvements.exterior_walls`
- `improvements.roof_structure`
- `improvements.hvac`
- `improvements.interior_finish`
- `improvements.site_improvements`

Template risk: high. Many fields repeat in salient facts, improvement detail, valuation grids, and reconciliation.

### `narrative.highest_and_best_use`

Purpose: apply legal permissibility, physical possibility, financial feasibility, and maximum productivity as vacant and as improved.

Inputs:

- `zoning.current_use_conformance`
- `site.size_acres`
- `site.access`
- `market.trend_summary`
- `subject.current_use`
- `hbu.as_vacant.*`
- `hbu.as_improved.*`

Template risk: high. Definition language is static, but conclusions must follow subject facts and valuation logic.

### `narrative.sales_comparison`

Purpose: explain comparable selection, verification, adjustment logic, adjusted range, and value conclusion.

Inputs:

- `sale_comps[]`
- `valuation.sales_comparison.unit_type`
- `valuation.sales_comparison.unit_value`
- `valuation.sales_comparison.indication`
- adjustment rationale fields

Template risk: high. Narrative should be controlled by grid data and appraiser-selected adjustment rationale.

### `narrative.income_approach`

Purpose: explain rent comparables, market rent, vacancy, expenses, NOI, capitalization rate, and income value conclusion, or why the approach is not developed.

Inputs:

- `valuation.income_approach.developed`
- `rent_comps[]`
- `valuation.income_approach.market_rent_psf`
- `valuation.income_approach.vacancy_rate`
- `valuation.income_approach.expense_ratio`
- `valuation.income_approach.noi`
- `valuation.income_approach.cap_rate`
- `valuation.income_approach.reason_not_developed`

Template risk: high. For retail, this is often the largest distinction between owner-occupied/single-tenant and leased/investment templates.

### `narrative.reconciliation`

Purpose: reconcile approach indications, explain weighting, and support the final value conclusion.

Inputs:

- `valuation.cost_approach.indication`
- `valuation.sales_comparison.indication`
- `valuation.income_approach.indication`
- `valuation.reconciliation.primary_approach`
- `valuation.reconciliation.supporting_approach`
- `valuation.final_value_rounded`

Template risk: very high. This block must mirror actual approach development and cannot be generic.

## 6. Static Boilerplate Candidates

These blocks appear to be stable legal, professional, or methodological text. They should generally be locked or maintained as controlled template text, not AI-edited in ordinary report generation.

- Market value definition and numbered conditions of sale.
- USPAP compliance framing.
- Standard assumptions and limiting conditions.
- Certification statements.
- No responsibility for legal or title considerations.
- Assumption of good and marketable title unless otherwise stated.
- Responsible ownership and competent management assumption.
- Reliance on information furnished by others without warranty.
- Engineering, plot plan, sketch, and illustrative exhibit disclaimers.
- Hidden conditions / subsoil / structural condition disclaimer.
- Environmental compliance assumption.
- Zoning and use regulation compliance assumption unless nonconformity is stated.
- Licenses, certificates of occupancy, and administrative approvals assumption.
- Boundary, encroachment, and trespass assumption.
- ADA compliance survey disclaimer.
- Mineral rights and personal property exclusion language.
- Allocation of value between land and improvements limitation.
- General cost approach theory and substitution principle.
- General sales comparison approach theory and substitution principle.
- Highest and best use definition from appraisal literature.
- Appraisal report reliance and distribution restrictions.

Recommended treatment:

- Store as versioned locked blocks.
- Require appraiser approval for any change.
- Track source/version/date of each static block.
- Expose only controlled toggles, such as include/exclude or restricted/full report variant.

## 7. Variable Boilerplate Candidates

These blocks use repeated structure but require property-specific facts, approach decisions, or market data. They are suitable for field-driven automation, but not uncontrolled AI rewriting.

- Scope of work inspection paragraph, especially inspected-by name and internal/external inspection extent.
- Data sources list.
- Comparable verification paragraph, including auditor/assessor/CoStar references.
- Approach applicability paragraph: which approaches are developed, not developed, and why.
- Market trend analysis using sector/submarket statistics.
- Neighborhood boundary and surrounding-use narrative.
- Zoning district and conformance discussion.
- Real estate tax and assessment summary.
- Site description paragraph and supporting site table.
- Improvement description paragraph and building detail table.
- Highest and best use as vacant and as improved conclusions.
- Sales comparison comparable selection and adjustment rationale.
- Income approach applicability, rent selection, capitalization, or omission rationale.
- Reconciliation approach weighting and final opinion support.
- Final statement of value with subject address, interest, date, and rounded value.

Recommended treatment:

- Generate from validated fields plus controlled sentence patterns.
- Preserve appraiser-selected conclusion phrases.
- Use AI only for drafting narrative from structured facts, with tracked review status.
- Add consistency checks across salient facts, approach tables, reconciliation, and final statement.

## 8. Subject-Specific Fields Commonly Repeated

The same facts recur in multiple report locations, which makes them strong candidates for a central field store.

- Address appears in cover, salient facts, scope, valuation sections, final statement, appendix labels, and comparable maps.
- Property type appears in salient facts, market section, HBU, improvement description, and approach applicability.
- Property rights appear in salient facts, valuation sections, comparable sale grids, and final statement.
- Date of value appears in salient facts, scope, valuation conclusions, certification, and final statement.
- Final value appears in salient facts, reconciliation, final statement, and sometimes transmittal text.
- Site size appears in salient facts, site description, HBU, land-to-building ratio, and comparable adjustment logic.
- Building size appears in salient facts, improvement section, sales comparison unit value, income approach, and grids.
- Year built and condition appear in improvement description and comparable adjustment rationale.
- Zoning code appears in salient facts, zoning section, HBU legal permissibility, and appendix labels.
- Tax parcel and assessment data appear in tax section, salient facts, appendix, and sometimes site identification.
- Inspection/appraiser names appear in scope, certification, and signature pages.
- Approach indications appear in salient facts, approach sections, reconciliation, and final value.

## 9. Appraiser / Author Style Observations

DOCX metadata commonly lists `Pamela Casper` as creator. The `lastModifiedBy` field often identifies a working appraiser or editor, including Abby Rossi, Chad DiSalle, Tracy Casper, Chris Rossi, Kady Weith, Michael Stout, Pam Casper, Mike Scannell, and Commercial.

Observed differences are present but narrower than expected because the report framework is strongly templated.

- Reports associated with Abby Rossi and Chad DiSalle show heavy adherence to the standard four-part structure and repeated boilerplate.
- Reports associated with Chris Rossi often include direct inspection phrasing that names the inspector in the scope section.
- Reports associated with Tracy Casper and Michael Stout show similar report architecture but may vary between first-person singular and team voice depending on report lineage.
- Some older or legacy reports use less consistent capitalization, page-numbered headings embedded in the table of contents, and more filename variation.
- First-person voice varies: some reports say "I personally reviewed" or "my investigation"; others say "we personally reviewed" or "our investigation." This should be normalized by appraiser role and signature structure.

Template implication:

- Do not infer writing style solely from metadata. Use signature block, certification, inspection sentence, and final statement voice together.
- Future templates should support `voice.first_person_singular` and `voice.first_person_plural` as controlled settings.
- Appraiser-specific style should be a light overlay, not separate templates, unless future extraction proves substantive differences.

## 10. Suggested First Commercial Retail Template Sections

The first commercial retail template should follow the dominant library order and support both owner-occupied and investment/income-producing retail assignments.

Recommended section set:

1. Cover / title page
2. Table of contents
3. Summary of Salient Facts / USPAP Compliancy
4. Scope of Work
5. Area Data
6. Neighborhood Description
7. Retail Market Trend Analysis
8. Zoning
9. Tax and Assessment Data
10. Site Description
11. Building Improvement Detail
12. Highest and Best Use Analysis
13. Cost Approach
14. Sales Comparison Approach
15. Income Approach - Direct Capitalization
16. Reconciliation and Final Value Estimate
17. Final Statement of Value
18. Assumptions and Limiting Conditions
19. Certification
20. Appendix

Recommended retail-specific modules:

- `retail.location_context`: arterial/corridor, corner influence, nearby anchors, visibility, access.
- `retail.trade_area`: neighborhood boundaries, demand drivers, surrounding uses.
- `retail.occupancy`: owner-occupied, single-tenant, multi-tenant, vacant, stabilized.
- `retail.site_utility`: frontage, depth, parking, ingress/egress, drive-thru, signage.
- `retail.improvement_utility`: showroom, restaurant, bar, service bays, kitchen, office, warehouse/back-of-house.
- `retail.market_conditions`: CoStar or appraiser market data.
- `retail.sales_comparison`: sale unit basis, adjustment grid, comparable narrative.
- `retail.income_applicability`: not developed, direct capitalization, market rent support, lease analysis.
- `retail.reconciliation`: approach weighting by occupancy and investment profile.

Initial template variants:

- Retail owner-occupied / single user: sales comparison primary; income not developed or secondary; cost often not developed.
- Retail leased / investment: sales comparison and income approach both developed; income may receive equal or greater weight.
- Restaurant / drive-thru: retail template plus specialized improvement fields for kitchen, dining, bar, drive-thru, and site circulation.
- Small downtown retail: stronger narrative for functional utility, parking limitations, mixed-use context, and HBU.

## 11. Field-Control Rules for Falcon Intelligence

Recommended controls for future report generation:

- Any value in the final statement must be sourced from `valuation.final_value_rounded`.
- Any date in final statement, scope, salient facts, and certification must source from `assignment.date_of_value` or `assignment.date_of_report`.
- Any address reference must source from canonical subject address fields, not typed narrative.
- Approach sections must be conditionally included or marked not developed based on `valuation.*.developed`.
- Reconciliation must be generated only after all developed approach indications are populated.
- HBU conclusions must be separately stored for as-vacant and as-improved states.
- Zoning conformance must require explicit appraiser confirmation.
- Market trend data must carry source and report date.
- Static boilerplate must be locked from ordinary AI edits.
- Appraiser voice must be selected before generating scope, verification, reconciliation, certification-adjacent prose, and final statement.

## 12. Risks and Uncertainties

- Filename classification is imperfect. Some completed reports may be named unusually, and some files with "report" in the name may be drafts or supporting documents.
- PDF-only reports were not the strongest source for this pass because DOCX files preserve report structure and metadata better.
- Some duplicate reports exist as original, revised, final, report-only, and complete versions. A future pass should select the latest authoritative version per assignment.
- Metadata author fields are not reliable enough by themselves to determine the signing appraiser or narrative style.
- Table of contents text can be mistaken for section body text during automated extraction.
- Report sections sometimes appear in different order for land, special-use, restricted, or income-focused assignments.
- Static boilerplate may contain legacy language that has changed over time. It should be legally/professionally reviewed before locking into Falcon templates.
- Market condition blocks are time-sensitive and may contain source-specific data that should not be generalized.
- Zoning, tax, flood, and HBU facts are high-risk fields and need validation against source documents.
- Retail and restaurant reports overlap heavily, but restaurant reports need extra improvement and site-circulation fields.

## 13. Recommended Next Extraction Pass

Recommended next pass:

1. Build a canonical completed-report selector.
2. Deduplicate report families and keep the latest completed version.
3. Extract DOCX body text, tables, core metadata, headings, and signature/certification blocks.
4. Extract PDF text only for reports with no DOCX source.
5. Create a section map for each report with page/order, heading, and body snippet.
6. Separate table-of-contents headings from actual body headings.
7. Build a field occurrence map showing where each subject fact repeats.
8. Compare revised versus final reports to identify appraiser edits and unstable template zones.
9. Create boilerplate fingerprints for static blocks and variable boilerplate patterns.
10. Build a retail-only gold set of 15 to 25 reports for the first Falcon template.
11. Review static boilerplate with the appraisal team before locking it.
12. Create a human-approved field dictionary with required, optional, and calculated fields.

Recommended gold-set categories for the first retail template:

- Single-tenant retail
- Multi-tenant retail strip center
- Restaurant / bar
- Drive-thru retail
- Small downtown storefront
- Owner-occupied retail
- Leased investment retail
- Restricted retail report, if Falcon must support restricted formats early

## 14. Proposed Template Build Sequence

1. Build locked static boilerplate library.
2. Build master field registry and validation rules.
3. Build salient facts generator.
4. Build site and improvement field-driven narratives.
5. Build zoning and tax modules.
6. Build retail market conditions module.
7. Build approach applicability logic.
8. Build sales comparison narrative from comparable grid data.
9. Build income approach narrative from rent and capitalization data.
10. Build reconciliation and final statement generator.
11. Add appraiser voice controls.
12. Test against the retail gold set and compare output to completed reports.

## 15. Immediate Falcon Intelligence Takeaways

- The report library is already highly templated, which is favorable for Falcon extraction and generation.
- The strongest first automation target is not freeform report writing; it is field synchronization across repeated facts.
- Static boilerplate should be locked early to prevent accidental AI changes to professional/legal language.
- Variable boilerplate should be generated from fields and appraiser-selected logic, not open-ended prompts.
- The first commercial retail template should be built as a modular retail shell with toggles for owner-occupied, leased investment, restaurant/drive-thru, and restricted-report variants.
- Appraiser style exists, but the larger control issue is report voice, approach selection, and consistency across repeated facts.
