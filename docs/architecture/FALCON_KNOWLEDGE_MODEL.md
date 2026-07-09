# Falcon Knowledge Model

This document defines the canonical object model for Falcon Intelligence knowledge. It is documentation-only and does not authorize database schema changes, production APIs, report ingestion, extraction, OCR, embeddings, OneDrive integration, source-document preview, or real data processing.

Knowledge objects are structured, tenant-scoped representations of verified appraisal knowledge. They are built from facts, relationships, evidence, confidence context, and audit history.

## Modeling Principles

- Knowledge objects are not raw documents.
- Knowledge objects are not extracted suggestions.
- Knowledge objects are composed from facts with verification state.
- Knowledge Object Builder V1 is the local bridge from Verified Facts into object candidates; production schemas and Memory Graph records come later.
- Every knowledge object belongs to one tenant.
- Every reusable object needs provenance, freshness, and permission context.
- Relationships are first-class because appraisal knowledge depends on context.
- Objects should support future expansion without forcing early implementation.

## Object Contract

Every canonical knowledge object should eventually support:

| Field family | Purpose |
| --- | --- |
| Identity | Stable tenant-scoped ID, display name, object type, aliases. |
| Classification | Property type, assignment type, evidence type, market category, or workflow category. |
| Core attributes | The verified facts that define the object. |
| Relationships | Links to properties, reports, evidence, people, markets, assignments, and derived records. |
| Trust context | Confidence, verification state, evidence support, conflicts, freshness, and audit references. |
| Lifecycle state | Suggested, in review, verified, rejected, superseded, archived, or policy-restricted. |
| Permission context | Visibility, reuse eligibility, client exposure policy, and role restrictions. |
| Expansion slots | Future fields, external references, AI assistance outputs, and jurisdiction-specific data. |

## Canonical Objects

### Property

Purpose: Represents a real property or property candidate known to the firm.

Primary attributes:

- Property ID.
- Tenant ID.
- Name or display label.
- Address.
- Parcel ID.
- Coordinates or location reference.
- Property type and subtype.
- Ownership interest.
- Site and improvement summaries.
- Current verification state.

Relationships:

- Reports.
- Assignments.
- Comparables.
- Parcel.
- Improvements.
- Inspections.
- Photos.
- Maps.
- Market and Neighborhood.
- Zoning and Flood records.
- Appraisers, reviewers, clients, and evidence links.

Future expansion notes: Property should become the main anchor for institutional knowledge, timelines, prior assignments, comparable reuse, map layers, relationship graphs, and future Falcon integration.

### Report

Purpose: Represents an appraisal report or report record as a source and context object.

Primary attributes:

- Report ID.
- Assignment ID.
- Tenant ID.
- Report type.
- Effective date.
- Report date.
- Client.
- Appraiser.
- Reviewer.
- Source document metadata.
- Report status.

Relationships:

- Property.
- Client.
- Appraiser.
- Reviewer.
- Source Evidence.
- Narrative.
- Certification.
- Extraordinary Assumptions.
- Hypothetical Conditions.
- Comparables, adjustments, income, expenses, maps, and photos referenced by the report.

Future expansion notes: Report objects should support provenance and workflow context before any report content is available. They should not become document viewers by default.

### Comparable

Purpose: Represents a reusable market evidence object that may be a sale, lease, listing, expense, or other comparable type.

Primary attributes:

- Comparable ID.
- Comparable type.
- Tenant ID.
- Related property.
- Effective or transaction date.
- Verification state.
- Freshness state.
- Reuse eligibility.
- Summary metrics relevant to the comparable type.

Relationships:

- Property.
- Sale.
- Lease.
- Adjustment.
- Market.
- Neighborhood.
- Report usage.
- Source Evidence.
- Appraiser and reviewer verification records.

Future expansion notes: Comparable is a parent abstraction. Specialized comparable types should hold domain-specific fields while sharing provenance, verification, conflict, and freshness behavior.

### Sale

Purpose: Represents a sale transaction used as evidence, subject history, or a sale comparable.

Primary attributes:

- Sale ID.
- Property ID.
- Sale date.
- Sale price.
- Buyer and seller treatment.
- Property rights conveyed.
- Financing terms.
- Conditions of sale.
- Price metrics.
- Verification and stale-after dates.

Relationships:

- Comparable.
- Property.
- Report.
- Parcel.
- Market.
- Adjustment.
- Source Evidence.
- Appraiser and reviewer records.

Future expansion notes: Sale records should support transaction verification, conflict detection, stale warnings, and promotion from subject history to firm-searchable comparable only after approval.

### Lease

Purpose: Represents lease evidence or a lease comparable.

Primary attributes:

- Lease ID.
- Property ID.
- Tenant name or confidential tenant reference.
- Lease date.
- Commencement date.
- Term.
- Rent.
- Rent basis.
- Escalations.
- Concessions.
- Expense structure.
- Verification state.

Relationships:

- Comparable.
- Property.
- Market.
- Income.
- Source Evidence.
- Report usage.
- Appraiser and reviewer records.

Future expansion notes: Lease objects need strong confidentiality and permission controls. Tenant identities and deal terms may require restricted visibility even inside a firm.

### Adjustment

Purpose: Represents a valuation adjustment concept, factor, or applied adjustment connecting comparable evidence to an appraisal analysis.

Primary attributes:

- Adjustment ID.
- Adjustment category.
- Basis.
- Direction.
- Amount or qualitative description.
- Source rationale reference.
- Applicable property or comparable.
- Verification state.

Relationships:

- Comparable.
- Sale or Lease.
- Report.
- Market.
- Narrative.
- Appraiser notes.
- Source Evidence.

Future expansion notes: Adjustment objects should preserve rationale and supporting evidence. They should not imply automated adjustment selection or valuation conclusions.

### Market

Purpose: Represents a market, submarket, or economic context used to organize property and comparable knowledge.

Primary attributes:

- Market ID.
- Name.
- Geography.
- Property type.
- Date range.
- Indicator summaries.
- Source count.
- Freshness state.
- Verification state.

Relationships:

- Neighborhood.
- Property.
- Comparables.
- Reports.
- Market indicators.
- Maps.
- Source Evidence.

Future expansion notes: Market objects should support verified observations, market-area layers, trend context, and future aggregate indicators without exposing confidential assignment details.

### Neighborhood

Purpose: Represents a smaller location context relevant to property analysis.

Primary attributes:

- Neighborhood ID.
- Name.
- Boundary reference.
- Market membership.
- Character summary.
- Access and amenity notes.
- Verification state.

Relationships:

- Market.
- Property.
- Maps.
- Reports.
- Comparables.
- Zoning and Flood context.

Future expansion notes: Neighborhood should support spatial context, local narratives, and relationship mapping while preserving source and freshness context.

### Reviewer

Purpose: Represents a person or role responsible for review activity.

Primary attributes:

- Reviewer ID.
- Tenant ID.
- Display name.
- Role.
- Review scope.
- Status.

Relationships:

- Reports.
- Verification records.
- Review History.
- Recommendations.
- Actions.
- Audit events.

Future expansion notes: Reviewer identity must eventually come from production identity systems. Synthetic preview values should remain clearly non-production.

### Client

Purpose: Represents the client connected to assignments, reports, and external deliverables.

Primary attributes:

- Client ID.
- Tenant ID.
- Display name.
- Client type.
- Access policy.
- Assignment relationship.

Relationships:

- Reports.
- Assignments.
- Properties.
- Appraisers.
- Client-visible deliverables.

Future expansion notes: Client objects require strict separation from internal firm intelligence. Internal knowledge, review notes, confidence context, and evidence should remain hidden unless explicitly shared.

### Appraiser

Purpose: Represents the professional responsible for appraisal work and verification decisions.

Primary attributes:

- Appraiser ID.
- Tenant ID.
- Display name.
- Role or credential context.
- Assignment scope.
- Status.

Relationships:

- Reports.
- Assignments.
- Verified facts.
- Recommendations acted on.
- Reviewers.
- Audit events.

Future expansion notes: Appraiser decisions remain the professional accountability layer for valuation-related facts, insight interpretation, and report use.

### Inspection

Purpose: Represents site inspection activity and inspection-derived facts.

Primary attributes:

- Inspection ID.
- Property ID.
- Inspection date.
- Inspector.
- Scope.
- Condition observations.
- Access limitations.
- Verification state.

Relationships:

- Property.
- Photos.
- Improvements.
- Report.
- Source Evidence.
- Appraiser.

Future expansion notes: Inspection objects should support timelines, condition changes, and evidence links without creating unsupported physical-condition conclusions.

### Photos

Purpose: Represents photo evidence metadata and relationships.

Primary attributes:

- Photo ID.
- Tenant ID.
- Property ID.
- Caption or label.
- Taken date.
- Source type.
- Access policy.
- Verification state.

Relationships:

- Property.
- Inspection.
- Improvements.
- Report.
- Source Evidence.

Future expansion notes: Photo content, image processing, and previews remain future gated capabilities. The object model should initially support metadata and evidence relationships.

### Maps

Purpose: Represents map exhibits, spatial references, or map layers connected to appraisal knowledge.

Primary attributes:

- Map ID.
- Map type.
- Geography.
- Layer references.
- Source.
- Date.
- Verification state.

Relationships:

- Property.
- Parcel.
- Market.
- Neighborhood.
- Flood.
- Zoning.
- Reports.

Future expansion notes: Maps should support workspace orientation and evidence context. Production map providers, GIS calculations, and live spatial services are separate future gates.

### Flood

Purpose: Represents flood-zone or flood-risk context connected to a property or site.

Primary attributes:

- Flood record ID.
- Property or parcel ID.
- Zone.
- Map panel reference.
- Effective date.
- Source.
- Verification state.

Relationships:

- Property.
- Parcel.
- Site.
- Maps.
- Report.
- Source Evidence.

Future expansion notes: Flood objects need source-date handling, conflict detection, and jurisdiction-specific expansion.

### Zoning

Purpose: Represents zoning classification and zoning-related context.

Primary attributes:

- Zoning record ID.
- Property or parcel ID.
- Zoning code.
- Jurisdiction.
- Permitted use summary.
- Source date.
- Verification state.

Relationships:

- Property.
- Parcel.
- Site.
- Market.
- Maps.
- Report.
- Source Evidence.

Future expansion notes: Zoning should support changes over time, legal nonconforming flags, entitlement references, and source freshness warnings.

### Parcel

Purpose: Represents parcel identity and land-record context.

Primary attributes:

- Parcel ID.
- Assessor parcel number.
- Legal description reference.
- Land area.
- Jurisdiction.
- Ownership reference.
- Verification state.

Relationships:

- Property.
- Site.
- Zoning.
- Flood.
- Maps.
- Reports.
- Source Evidence.

Future expansion notes: Parcel can support multiple-property relationships, assemblages, splits, and public-record cross-checks after appropriate gates.

### Improvements

Purpose: Represents buildings and physical improvements on a property.

Primary attributes:

- Improvement ID.
- Property ID.
- Building type.
- Year built.
- Renovation year.
- GLA, NRA, units, or other area basis.
- Condition.
- Quality.
- Stories.
- Parking and amenity summary.
- Verification state.

Relationships:

- Property.
- Inspection.
- Photos.
- Report.
- Comparable.
- Adjustment.
- Source Evidence.

Future expansion notes: Improvements should track changes over time, measurement basis, conflicting values, and source-specific limitations.

### Income

Purpose: Represents income-related facts and structured income evidence.

Primary attributes:

- Income ID.
- Property ID.
- Income type.
- Amount.
- Unit basis.
- Period.
- Occupancy context.
- Source type.
- Verification state.

Relationships:

- Property.
- Lease.
- Report.
- Market.
- Expenses.
- Narrative.
- Source Evidence.

Future expansion notes: Income objects require confidentiality controls and should distinguish property-specific evidence from market-level indicators.

### Expenses

Purpose: Represents operating expense facts, benchmarks, or comparable expense evidence.

Primary attributes:

- Expense ID.
- Property or market context.
- Expense category.
- Amount.
- Unit basis.
- Period.
- Source type.
- Verification state.

Relationships:

- Property.
- Income.
- Market.
- Report.
- Comparable.
- Source Evidence.

Future expansion notes: Expenses may become property-specific, comparable-specific, or aggregate market indicators. Permission and aggregation rules should be explicit.

### Narrative

Purpose: Represents approved narrative structures, summaries, or report-section support derived from verified structured inputs.

Primary attributes:

- Narrative ID.
- Report ID.
- Section type.
- Approved summary reference.
- Source facts.
- Review state.

Relationships:

- Report.
- Property.
- Market.
- Adjustments.
- Certification.
- Extraordinary Assumptions.
- Hypothetical Conditions.
- Source Evidence.

Future expansion notes: Narrative should be generated or drafted only from approved structured inputs and appraiser-controlled rationale. It must not rely on unverified source text.

### Certification

Purpose: Represents report certification context and professional responsibility statements.

Primary attributes:

- Certification ID.
- Report ID.
- Certifying appraiser.
- Reviewer or supervisory context.
- Date.
- Certification type.
- Verification state.

Relationships:

- Report.
- Appraiser.
- Reviewer.
- Client.
- Audit events.

Future expansion notes: Certification objects require strict role, signature, and compliance controls. They should not be modified by automated intelligence features.

### Extraordinary Assumptions

Purpose: Represents extraordinary assumptions associated with a report, property, or analysis.

Primary attributes:

- Assumption ID.
- Report ID.
- Text reference or structured summary.
- Affected analysis area.
- Responsible appraiser.
- Review state.

Relationships:

- Report.
- Property.
- Narrative.
- Certification.
- Reviewer notes.
- Source Evidence.

Future expansion notes: Extraordinary assumptions should be visible in insight and recommendation logic as professional constraints, not machine-resolved issues.

### Hypothetical Conditions

Purpose: Represents hypothetical conditions associated with a report, property, or analysis.

Primary attributes:

- Condition ID.
- Report ID.
- Structured summary.
- Affected analysis area.
- Responsible appraiser.
- Review state.

Relationships:

- Report.
- Property.
- Narrative.
- Certification.
- Reviewer notes.
- Source Evidence.

Future expansion notes: Hypothetical conditions should influence insight context and recommendation wording so the system does not treat hypothetical facts as ordinary verified facts.

## Relationship Types

The canonical model should support these relationship types:

| Relationship | Meaning |
| --- | --- |
| Supports | Evidence supports a fact, object, insight, or recommendation. |
| Conflicts with | One fact or object conflicts with another and needs review. |
| Supersedes | A newer verified object replaces an older one. |
| Derived from | A knowledge object or insight is derived from facts or other knowledge objects. |
| Used in | A fact, comparable, or object was used in a report, assignment, or action. |
| Reviewed by | A person reviewed the object or related recommendation. |
| Verified by | A person verified the fact or object. |
| Located in | A property belongs to a parcel, neighborhood, market, or geography. |
| Constrained by | A report or analysis is constrained by assumptions, conditions, policy, or permission. |

## Current Guardrail

This object model is a canonical architecture reference only. It does not create tables, APIs, extraction targets, production contracts, or UI implementation requirements. Future schema and implementation work must pass separate gates and remain aligned with the Intelligence Engine hierarchy.
