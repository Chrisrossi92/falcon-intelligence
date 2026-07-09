# Falcon Intelligence Engine

This document defines the canonical Intelligence Engine architecture for Falcon Intelligence. It is documentation-only. It does not authorize OCR, embeddings, report ingestion, source-document preview, OneDrive integration, Supabase changes, backend APIs, production data access, or extraction pipelines.

Falcon Intelligence is not a document viewer. It is the premium intelligence layer that turns appraisal work into structured, tenant-scoped organizational knowledge.

## Canonical Hierarchy

Every future Falcon Intelligence capability should preserve this hierarchy:

```text
Documents
-> Facts
-> Knowledge
-> Insights
-> Recommendations
-> Actions
```

The hierarchy is permanent product architecture, not a temporary workflow. It separates what a source says, what the firm has verified, what the system can infer, what it recommends reviewing, and what an operator may choose to do.

## Intelligence Lifecycle

The canonical lifecycle is:

```text
Source Evidence
-> Extracted Facts
-> Verified Facts
-> Knowledge Objects
-> Insight Generation
-> Recommendations
-> Operator Actions
```

Each layer has a distinct purpose and owner.

| Layer | Purpose | Primary owner | Product rule |
| --- | --- | --- | --- |
| Source Evidence | Identifies the material, metadata, record, or approved reference that supports a future fact. | Firm policy and authorized users. | Evidence may be referenced before source preview exists, but it must remain metadata-only until a separate source-access gate approves more. |
| Extracted Facts | Candidate statements proposed from user entry, metadata, future extraction, or controlled AI assistance. | System as drafter; human as reviewer. | Extracted facts are never firm knowledge by themselves. They are suggestions requiring verification. |
| Verified Facts | Individual facts accepted, edited, rejected, or deferred by an authorized appraiser, reviewer, admin, or owner under firm policy. | Authorized human verifier. | Verification state is mandatory before reuse, search promotion, or downstream insight generation. |
| Knowledge Objects | Tenant-scoped structured objects composed from verified facts and relationships. | Firm knowledge model and governance policy. | Knowledge Object Builder V1 defines the local promotion discipline before any future Memory Graph or production schema exists. |
| Insight Generation | Analysis that interprets verified knowledge patterns, gaps, conflicts, or operational context. | Intelligence Engine with human accountability. | Insights must remain explainable and traceable to knowledge and evidence; they must not become automated valuation conclusions. |
| Recommendations | Suggested next review step, verification step, workflow route, or evidence inspection. | Intelligence Engine as advisor; appraiser/reviewer as decision-maker. | Recommendations guide attention. They do not select comps, make value conclusions, or replace professional judgment. |
| Operator Actions | Concrete UI or workflow action the user may choose to take. | Appraiser, reviewer, admin, or owner. | Actions must respect role permissions, assignment context, audit requirements, and production gates. |

## Layer Definitions

### Documents

Documents are possible source containers, not the product's center of gravity.

Examples include reports, addenda, leases, operating statements, maps, photos, certificates, public records, and appraiser workpapers. In the current repository, document handling remains blocked except for metadata-only concepts already documented elsewhere.

Architectural rule: a document may support intelligence, but Falcon Intelligence should not force users to browse documents to understand the firm's knowledge. The system should surface structured knowledge with evidence paths.

### Facts

Facts are atomic claims that can be checked, corrected, verified, rejected, or superseded.

Examples:

- A building year.
- A parcel identifier.
- A lease term.
- A sale date.
- A zoning classification.
- A reviewer approval state.

Architectural rule: facts are not insights. They describe a value, observation, or status. They should carry evidence, verification state, freshness, conflict state, and audit history.

### Knowledge

Knowledge is a structured representation of what the firm accepts as usable institutional context.

Knowledge is built from verified facts and relationships. A Property object, Comparable object, Market object, Report object, or Adjustment object is knowledge only when its facts and relationships are governed by verification and trust rules.

Architectural rule: knowledge objects are the stable foundation for future AI capabilities. AI features should consume knowledge objects before relying on raw documents, free text, or unverified suggestions.

Current implementation boundary: Knowledge Object Builder V1 creates local object candidates from Verified Facts only. Memory Graph Prototype V1 connects those candidates into local nodes and relationships. These are bridges to future durable knowledge, not production graphs, APIs, or database schemas.

### Insights

Insights interpret knowledge in context. They answer what the verified knowledge may mean for the current appraisal workflow, review workflow, or firm knowledge base.

Insights may identify:

- Consistency or inconsistency.
- Freshness risk.
- Relationship patterns.
- Missing evidence.
- Similar prior work.
- Possible review areas.
- Knowledge gaps.

Architectural rule: insights must be derived from known inputs and must expose their reasoning path at a product level. They should not appear as unexplained AI answers.

### Recommendations

Recommendations translate insights into suggested next steps.

Recommendations may suggest:

- Review a section.
- Inspect supporting evidence.
- Reverify a stale comparable.
- Request reviewer approval.
- Compare conflicting facts.
- Open a related knowledge object.
- Defer reuse until evidence is stronger.

Architectural rule: recommendations should be phrased as review guidance, not as final appraisal decisions.

### Actions

Actions are operator-controlled workflow steps. They are the only layer where Falcon Intelligence should move from advice to user choice.

Actions may include:

- Open a Passport.
- Open Supporting Evidence.
- Open Review History.
- Start verification.
- Request review.
- Mark a fact rejected.
- Add an appraiser note.
- Navigate to a report section when source access is approved.

Architectural rule: every meaningful action should preserve context, permissions, and auditability.

## Ownership Model

Ownership separates system drafting from professional accountability.

| Responsibility | Owner |
| --- | --- |
| Tenant data ownership | Appraisal firm. |
| Source approval policy | Firm owner/admin with appraiser/reviewer input. |
| Extracted fact proposals | Future controlled system process or authorized user. |
| Fact verification | Authorized appraiser, reviewer, admin, or owner under policy. |
| Knowledge object governance | Firm policy and canonical knowledge model. |
| Insight generation rules | Falcon Intelligence architecture and product policy. |
| Recommendation display | Falcon Intelligence workspace surfaces. |
| Final appraisal judgment | Appraiser. |
| Review judgment | Reviewer under firm policy. |
| Audit and accountability | Falcon platform controls. |

## Why Future Capabilities Must Build Here

This model is the foundation for future AI work because it creates durable separation between:

- Source material and structured claims.
- Suggested facts and verified facts.
- Knowledge and interpretation.
- Interpretation and recommended workflow.
- Recommended workflow and human action.

Without this separation, future AI features would be hard to audit, hard to trust, hard to permission, and easy to confuse with automated appraisal judgment.

Every future capability should declare which layer it reads from, which layer it writes to, and which human approval path controls promotion to the next layer.

## Workspace Integration

The existing Intelligence Workspace preview should eventually display the hierarchy as product surfaces:

| Engine concept | Workspace placement |
| --- | --- |
| Documents / Source Evidence | Supporting Evidence drawer, metadata-only until source access is approved. |
| Facts | Passport fact summary and future fact-level detail rows. |
| Knowledge Objects | Map markers, synchronized table rows, Knowledge Summary, Passport identity, and the synthetic Property Passport Knowledge Objects Preview. |
| Insights | Insight cards or a compact insight strip tied to the selected knowledge object. |
| Recommendations | Recommendation panel inside the selected workspace context. |
| Actions | Clear operator-controlled buttons such as Open Passport, Review Evidence, Request Review, or Open Section when approved. |
| Confidence and verification | Badges, dimensions, warnings, and drill-down context near facts, insights, and recommendations. |
| Relationships | Knowledge relationship panel, map layers, and Passport cross-links. |

The workspace should keep the current product stance: calm, professional, traceable, and not a generic AI dashboard.

### Current Synthetic Insight Layer Preview

The React Intelligence Workspace preview now includes a synthetic, read-only Insight Layer Preview that makes the hierarchy visible for stakeholder review.

The preview maps the engine hierarchy as follows:

| Engine layer | Preview expression |
| --- | --- |
| Facts | Related fact chips and the first step in the Facts to Knowledge to Insight chain. |
| Knowledge | Selected property context, Passport-backed knowledge, and relationship-chain knowledge statements. |
| Insights | Compact synthetic insight cards for the selected workspace record. |
| Recommendations | Operator-facing recommendation panel tied to the selected insight. |
| Actions | Existing operator-controlled actions such as Open Passport and View supporting evidence. |
| Confidence / evidence | Synthetic trust badges and metadata-only evidence drill-down preview. |

This preview is local frontend product demonstration only. It does not run real AI, score confidence, parse source documents, call APIs, persist insight records, or create production schemas.

## Relationship to Existing Documents

This document is the canonical foundation for future AI and intelligence architecture. More specific documents should align to it:

- `docs/architecture/FALCON_KNOWLEDGE_MODEL.md` defines the canonical object model.
- `docs/architecture/FALCON_INSIGHT_ENGINE.md` defines how facts and knowledge become insights, recommendations, and actions.
- `docs/architecture/FALCON_CONFIDENCE_MODEL.md` defines the trust model for facts, knowledge, insights, and recommendations.
- `docs/data-confidence-provenance-model.md` remains the current detailed provenance and passport design.
- `docs/appraisal-intelligence-data-model.md` remains the earlier future verified intelligence data model and should be interpreted through this hierarchy.
- `docs/intelligence-workspace-map-experience.md` remains the current workspace UX specification.

## Current Guardrail

This is product architecture only. The current repository remains limited to documentation, safety checks, synthetic fixtures, metadata-only concepts, and preview contracts. Do not implement extraction systems, OCR, embeddings, production APIs, OneDrive integration, Supabase schema changes, real report processing, source-document preview, or production data handling from this document.
