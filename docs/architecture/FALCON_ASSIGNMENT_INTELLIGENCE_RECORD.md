# Falcon Assignment Intelligence Record V1

The Assignment Intelligence Record is the canonical, assignment-scoped view of what Falcon Intelligence observed, what an appraiser or reviewer decided, what evidence supports the current facts, and what remains unresolved before later analysis or report assistance.

V1 is a synthetic/local contract. It is not a production database, report writer, valuation engine, live Falcon integration, source-document viewer, or authorization system.

## Position in the Product Loop

```text
Falcon assignment reference + controlled source evidence
-> extracted candidate assertions
-> deterministic machine assessment
-> appraiser/reviewer decisions
-> canonical Assignment Intelligence Record
-> later analysis, narrative assistance, and QC
-> reusable firm knowledge
```

Falcon remains the owner of orders, operational status, users, permissions, assignment delivery, and client-facing operations. Falcon Intelligence stores only a narrow `EntityReference` for the Falcon assignment. It does not copy the operational order model.

## Existing-Model Audit

| Existing concept | Authoritative implementation | Current purpose | V1 treatment | Duplication or contradiction risk |
| --- | --- | --- | --- | --- |
| Assignment discovery | `src/falcon_intel/discovery.py` | Infers probable assignment folders from metadata. | Referenced as an upstream discovery aid only. | A discovered folder is not an operational assignment or canonical record identity. |
| Assignment profile | `src/falcon_intel/profile.py` | Exports metadata-only assignment folder summaries. | Kept separate; may later supply safe source metadata. | Its folder label must not become a Falcon assignment ID. |
| Historical intake | `src/falcon_intel/historical_intake.py` | Groups local historical files and likely final reports. | Reused as the upstream document-selection boundary. | Candidate order groups are probabilistic, not live Falcon orders. |
| Extracted candidates | `src/falcon_intel/historical_knowledge.py` | Produces deterministic metadata candidates with method and source hints. | Adapted directly through `build_candidate_evidence_bundle`. | Extraction confidence must not be confused with human acceptance. |
| Deterministic verification ledger | `src/falcon_intel/verification_engine.py` | Tests agreement, normalization, conflicts, and missing values. | Reused as `machine_verification_status` and `machine_confidence` on candidates. | Its historical name `VerifiedFact` does not imply an appraiser decision inside this contract. Only a review event creates a canonical fact. |
| Evidence links | `src/falcon_intel/evidence_link.py` | Metadata-only future navigation pointers. | Kept separate; AIR evidence is immutable assertion provenance and may reference the same source-document identity. | UI navigation status and assertion support are different concerns. |
| Data passports | `src/falcon_intel/data_passport.py` | Per-fact trust-card projection for UI. | Referenced/derived later from canonical facts; not embedded wholesale. | Passport verification enums are a display contract and do not replace record review history. |
| Corrections and audit | `src/falcon_intel/correction_audit.py` | Synthetic field correction history and current-value resolution. | Semantics adapted into append-only `ReviewEvent` plus fact revisions and explicit supersession. | The demo correction objects use a narrower target model and camel-case UI payload, so they remain separate. |
| Report Field Registry | `src/falcon_intel/report_registry.py` | Dot-key subject profile and report-merge readiness preview. | Dot-key convention reused; AIR readiness is broader and evidence-aware. | Registry `approved`/`locked` states cannot substitute for candidate, fact, conflict, or conclusion states. |
| Property Library | `src/falcon_intel/property_library.py` | Synthetic canonical property, evidence event, usage, and normalization candidates. | Canonical property IDs are referenced through `EntityReference`. | Copying the entire property record into every assignment would create identity drift. |
| Comparables | `src/falcon_intel/property_library.py`, `src/falcon_intel/intelligence_matcher.py`, and `src/falcon_intel/historical_comp.py` | Synthetic property usages, matching, and reuse justification. | Bounded `ComparableReference` stores identity, selection state, evidence IDs, and adjustment/qualitative-reference IDs only. | A match is not a selected comparable; selection is not an adjustment or value conclusion. |
| Knowledge Objects | `src/falcon_intel/knowledge_objects.py` | Builds local Property, Report, Client/User, Personnel, and Open Issues candidates from machine ledgers. | Referenced through `KnowledgeReference`; useful source identities and fact lineage may be promoted later. | Object candidates are not durable production knowledge and must not be copied as canonical facts. |
| Memory Graph | `src/falcon_intel/memory_graph.py` | Connects local Knowledge Object candidates. | Kept separate and referenced by stable knowledge IDs when useful. | Graph readiness is object-relationship readiness, not assignment analysis readiness. |
| Report sections | `src/falcon_intel/report_registry.py` and architecture documents | Organizes structured report-use fields and future narrative areas. | `ReportSectionReference` links fact and conclusion IDs without embedding narrative bodies. | A report section reference is not generated report language. |
| Falcon API boundaries | `src/falcon_intel/falcon_api_contract.py`, `falcon_passport_contract.py`, and `falcon_evidence_contract.py` | Local synthetic envelopes for card, Passport, and evidence workflows. | Kept separate; future Falcon exchange may carry the AIR V1 payload after auth and persistence gates. | Local response wrappers are not production APIs or authorization. |
| CLI/export patterns | `src/falcon_intel/cli.py` and existing `save_*_outputs` helpers | JSON previews and ignored local artifacts. | AIR provides deterministic `to_json`, `from_json`, and `save_assignment_intelligence_record`; no new CLI command is added in V1. | Saved records must remain under ignored local output paths and must never contain real source content in this slice. |

## Identity Distinctions

| Identity | Meaning in V1 |
| --- | --- |
| Operational assignment | Falcon-owned assignment/order reference. AIR stores only a narrow external reference when available. |
| Intelligence record | Stable `record_id` plus immutable `record_version`, schema version, timestamps, lifecycle, and lineage. |
| Property | Canonical Property Library or future production property ID referenced by `property_reference`. |
| Document/source | `SourceReference` with safe metadata, source ID, and optional document ID. Source content is not embedded. |
| Evidence | Immutable `EvidenceReference` pointing to a source, locator, extraction method, timestamp, confidence, and extractor version. |
| Candidate assertion | Machine observation grouped by canonical field and normalized value. It is never automatically a current fact. |
| Canonical fact | Appraiser-verified, appraiser-corrected, or appraiser-entered fact revision. Current facts are explicitly identified. |
| Appraiser conclusion | Separately authored professional judgment linked to facts/evidence; never stored in the fact ledger. |
| Comparable | External comparable identity referenced with candidate/selected state and support references. |
| Knowledge object | Reusable property, report, market, comparable, or graph object referenced rather than copied. |

## Contract Sections

| Section | Purpose |
| --- | --- |
| `identity` | Stable record ID, record/schema versions, timestamps, lifecycle, and previous-version lineage. |
| `tenant_id` | Firm isolation key retained by Falcon Intelligence. |
| `local_assignment_key` | Stable local fallback when a Falcon assignment reference is unavailable. |
| `falcon_assignment_reference` | Narrow Falcon-owned assignment identity; no order workflow fields are duplicated. |
| `sources` | Metadata-only document/source identities. |
| `evidence` | Immutable provenance and structured source locators. |
| `candidates` | Machine observations and deterministic machine assessment. |
| `review_events` | Append-only appraiser/reviewer decisions with actor, time, reason, prior/result values, and evidence IDs. |
| `facts` | All canonical fact revisions, including superseded history. |
| `current_fact_ids` | Explicit current view over the fact ledger. |
| `conflicts` | Resolved and unresolved disagreements with candidate/evidence lineage. |
| `assignment_context` | References to current assignment/report facts and assignment contacts. |
| `subject_property` | Canonical property reference, identity fact IDs, typed characteristic groups, and ownership references. |
| `comparable_references` | Candidate/selected comparable identities and bounded support references. |
| `market_references` | Market-observation or market-object references. |
| `prior_knowledge_references` | Prior-firm knowledge and Memory Graph references. |
| `report_section_references` | Future report-section links to facts/conclusions without narrative bodies. |
| `conclusions` | Explicit appraiser-authored conclusions, separate from facts. |
| `readiness` | Deterministic overall, area-level, blocking, and nonblocking readiness issues. |

## Canonical Field Dictionary

V1 uses dot-notation keys and a fact ledger rather than a giant flat property schema.

### Assignment context

- `assignment.client`
- `assignment.intended_user`
- `assignment.intended_use`
- `assignment.appraisal_purpose`
- `assignment.interest_appraised`
- `assignment.effective_date_requirement`
- `assignment.report_date_requirement`
- `assignment.due_date`
- `assignment.inspection_requirements`
- `assignment.inspection_date`
- `assignment.report_format`
- `assignment.engagement_constraints`
- `assignment.signing_appraiser`
- `assignment.reviewer`

Contacts are `EntityReference` values because Falcon owns user/contact identity.

### Subject identity

- `subject.property_id`
- `subject.name`
- `subject.address`
- `subject.parcel_identifiers`
- `subject.coordinates`
- `subject.property_type`
- `subject.property_subtype`
- `subject.alternate_identifiers`

Canonical property and ownership entities remain references. Identity facts provide assignment-specific evidence and review state.

### Typed subject characteristics

Common extensible keys include:

- `subject.site_area`
- `subject.building_area`
- `subject.year_built`
- `subject.units`
- `subject.occupancy`
- `subject.tenancy`
- `subject.zoning`
- `subject.flood`
- `subject.taxes`
- `subject.sale_history`
- `subject.renovation_history`
- `subject.construction`
- `subject.condition`
- `subject.access`
- `subject.visibility`
- `subject.utilities`
- `subject.parking`
- `subject.income`
- `subject.operating_information`

Each fact declares `category`, `value_type`, optional `unit`, materiality, origin, evidence, review events, and supersession. New property-specific keys can be added without changing a monolithic property object.

## State and Transition Semantics

```text
machine observation
    -> extracted_candidate
    -> accepted ---------> verified canonical fact
    -> corrected --------> corrected canonical fact; original candidate/evidence retained
    -> rejected ---------> no current fact; candidate and review event retained
    -> deferred ---------> no current fact; candidate and defer event retained for later review
    -> unresolved_conflict until competing values are explicitly resolved

appraiser entry ----------> appraiser_entered canonical fact + audit event
later accepted revision --> prior canonical fact becomes superseded
appraiser conclusion -----> conclusions collection only; never promoted from field completeness
```

Important distinctions:

- The existing deterministic Verification Engine supplies a machine assessment. It does not create a human-approved AIR fact.
- A `candidate_verified` review event promotes a candidate.
- A `candidate_corrected` event preserves the candidate value and evidence while creating a corrected current fact.
- A `candidate_rejected` event preserves the observation and rejection reason but removes it from the current-fact view.
- A `candidate_deferred` event preserves the observation and records the pause without promoting or rejecting it; readiness continues to surface the item.
- A conflict remains `unresolved` until one competing value is accepted/corrected and every other competing value is explicitly rejected.
- Corrections are additive. New fact revisions point to the fact they supersede; previous revisions remain in `facts` with state `superseded`.
- Appraiser-entered facts use their append-only review event as a basis even when no machine candidate exists.
- Conclusions require an explicit appraiser action and remain structurally separate from observations and facts.

## Embedded Versus Referenced

AIR embeds only the information required to understand assignment truth and its audit trail:

- Small metadata-only source identities.
- Immutable evidence metadata and locators.
- Candidate assertions.
- Fact revisions.
- Review events, conflicts, readiness issues, and explicit conclusions.

AIR references rather than duplicates:

- Falcon orders, users, permissions, contacts, workflow, and delivery.
- Canonical Property Library records and ownership entities.
- Detailed comparable/property records.
- Adjustment and qualitative-comparison records.
- Market observations and indicators.
- Data Passport UI projections.
- Knowledge Objects and Memory Graph nodes/relationships.
- Report section bodies and narrative text.

## Evidence and Provenance

Every promoted machine candidate retains:

- Source/document identity.
- Stable evidence identity.
- Page and section locator when available; table, cell, paragraph, and region slots are available for later approved sources.
- Extraction method and timestamp.
- Extraction confidence and source quality.
- Extractor name and version.
- Original source-field key and candidate reference.

`source_excerpt` exists in the contract but remains `null` in the V1 adapter. Safe source metadata is sufficient for this synthetic slice. Populating real excerpts or source previews remains gated.

## Analysis Readiness

Default V1 requirements are deliberately small:

| Area | Required fields | Severity |
| --- | --- | --- |
| Assignment context | Client, intended user, intended use, interest appraised, effective-date requirement | Blocking |
| Subject identity | Address and property type | Blocking |
| Site | Site area | Nonblocking |
| Improvements | Building area | Nonblocking |
| Professional review | Signing appraiser | Nonblocking |

The calculator also surfaces:

- Missing required facts.
- Unresolved conflicts.
- Unverified material candidates.
- Current facts supported only by weak evidence.
- Current facts supported by stale evidence.

An area is `blocked` when it has a blocking issue, `needs_review` when only nonblocking issues remain, and `ready` when it has no issues. Overall status follows the same precedence. Readiness is workflow completeness only. It does not generate or validate appraisal conclusions.

Requirements are explicit inputs so a later property type, report format, client scope, or firm policy can select a governed requirement set without changing fact semantics.

## Synthetic Vertical Proof

`src/falcon_intel/synthetic_assignment_record.py` creates a commercial industrial assignment using committed code-only synthetic text. It passes two synthetic pages through `extract_report_metadata_from_pages`, adapts the existing Verification Engine output, records appraiser and reviewer actions, and assembles the record.

The proof includes:

- Example Regional Bank as client and intended user.
- Loan-underwriting versus internal-planning intended-use conflict.
- 800 Meridian Commerce Drive as the synthetic subject.
- Industrial property type corrected to Industrial / Warehouse.
- 6.25 acres and 48,000 square feet as appraiser-entered typed facts.
- Leased fee interest and an effective-date requirement.
- Signing-appraiser verification and rejection of an inapplicable historical reviewer candidate.
- Selected sale and candidate lease comparable references.
- Market and prior-firm knowledge references.

Condensed deterministic payload excerpt (the complete serializer adds the referenced ledgers):

```json
{
  "identity": {
    "record_id": "air-962cf1c1bd0ec8a404c7",
    "record_version": 1,
    "schema_version": "1",
    "created_at": "2026-09-03T14:00:00+00:00",
    "updated_at": "2026-09-03T14:30:00+00:00",
    "lifecycle_state": "in_review",
    "lineage": {
      "previous_record_id": null,
      "previous_record_version": null
    }
  },
  "falcon_assignment_reference": {
    "display_label": "Synthetic Falcon assignment AIR-001",
    "reference_id": "falcon-order-synthetic-air-001",
    "reference_type": "falcon_assignment",
    "source_system": "falcon"
  },
  "conflicts": [
    {
      "conflict_id": "conflict-31561a5663aabb249bbd",
      "field_key": "assignment.intended_use",
      "status": "unresolved"
    }
  ],
  "readiness": {
    "overall_status": "blocked",
    "blocking_issue_ids": [
      "issue-522b440afbfdedd5eed8",
      "issue-a3118c272c677340178a"
    ]
  },
  "conclusions": []
}
```

The complete serializer includes all evidence, candidates, facts, review history, references, and readiness details. `scripts/smoke_assignment_intelligence_record.py` proves that repeated builds and a JSON round trip are equivalent.

## Falcon Integration Boundary

Future Falcon exchange should provide:

- Tenant and authorized assignment identity.
- Actor identity and role after production permission checks.
- Operational due date, contacts, and workflow context as references or approved fact proposals.
- Durable audit persistence for review actions.

Falcon Intelligence should return the versioned AIR contract or a narrower projection. Falcon remains authoritative for authorization, assignment status, user membership, client delivery, and operational workflow. No live integration is implemented in V1.

## Non-Goals and Deferred Decisions

V1 does not implement:

- Production persistence or database migrations.
- Live Falcon APIs, authentication, or permission changes.
- Real-document ingestion, cloud ingestion, OCR expansion, embeddings, or source preview.
- Narrative generation, valuation conclusions, automated comparable selection, or adjustment logic.
- A complete schema for every property type.
- Automatic property identity merge or comparable promotion.
- Firm-specific readiness policy selection.
- Durable Data Passport, Knowledge Object, or Memory Graph promotion.

Production choices for storage, event concurrency, access control, retention, redaction, and contract transport remain deferred behind the existing readiness gates.

## Implemented Downstream Slice

The synthetic/local appraiser-reviewed assignment/property brief workflow is implemented in `src/falcon_intel/local_intake_review.py` and `src/falcon_intel/assignment_brief.py`, with architecture details in `FALCON_LOCAL_INTAKE_REVIEW_AND_BRIEF.md`.

It adds accept, correct, reject, defer, conflict resolution, manual facts, review progress, readiness/blocker views, the versioned React adapter, and deterministic safe AIR/brief exports. It remains synthetic/local until production gates authorize real assignment documents, Falcon auth, persistence, and source access.
