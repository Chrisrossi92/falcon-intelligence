# Falcon Memory Graph

The Falcon Memory Graph is the institutional memory layer that connects verified appraisal knowledge across properties, reports, clients, personnel, issues, evidence, and future time-based history.

Memory Graph Prototype V1 is local and deterministic. It does not create a production graph database, Supabase schema, backend API, embeddings, vector search, AI output, OCR output, uploads, or real report ingestion.

## Position in the Intelligence Engine

```text
Documents
-> Candidate Facts
-> Verified Facts
-> Knowledge Object Candidates
-> Memory Graph
-> Insights
-> Recommendations
-> Actions
```

The Memory Graph answers:

```text
How are these appraisal knowledge objects connected?
```

It does not answer valuation questions, select comparables, or replace appraiser judgment.

## Purpose

Knowledge Objects describe individual things Falcon knows. The Memory Graph describes how those things relate.

The graph creates institutional memory by preserving:

- Which reports belong to a property.
- Which client or intended user is tied to a report.
- Which appraiser and reviewer are tied to a report.
- Which open issues prevent durable promotion.
- Which report supports the current Property Passport view.
- Which verified identity facts anchor a property memory.

## V1 Node Model

Each local node contains:

- Node id.
- Node type.
- Label.
- Source Knowledge Object id.
- Readiness.
- Confidence.
- Key attributes.
- Notes.

V1 node types:

- Property.
- Report.
- Client/User.
- Personnel.
- Open Issues.

## V1 Relationship Model

Each local relationship contains:

- Relationship id.
- Relationship type.
- From node id.
- To node id.
- Confidence.
- Source object references.
- Source fact references.
- Notes.

V1 relationship types:

| Relationship | Meaning |
| --- | --- |
| `PROPERTY_HAS_REPORT` | A Property node is connected to a Report node. |
| `REPORT_FOR_CLIENT` | A Report node is connected to the Client/User object through client facts. |
| `REPORT_HAS_INTENDED_USER` | A Report node is connected to the intended user when that relationship is usable. |
| `REPORT_PREPARED_BY_APPRAISER` | A Report node is connected to Personnel through appraiser facts. |
| `REPORT_REVIEWED_BY_REVIEWER` | A Report node is connected to Personnel through reviewer facts. |
| `REPORT_HAS_OPEN_ISSUE` | A Report node is connected to unresolved conflicts, missing fields, or review items. |
| `PROPERTY_HAS_VERIFIED_IDENTITY` | A Property node is anchored by verified or probable identity facts. |
| `REPORT_SUPPORTS_PROPERTY_PASSPORT` | A Report node supports the current Property Passport view. |

## Graph Readiness

Graph readiness is deterministic and inherited from node readiness:

- `ready`: all nodes are ready.
- `probable`: no blocked or needs-review nodes exist, but at least one node is probable.
- `needs_review`: no node is blocked, but at least one node needs review.
- `blocked`: at least one node is blocked.

Examples:

- If the Property node is blocked, the graph is blocked.
- If Open Issues contains conflicting critical facts, the graph is blocked.
- If only reviewer metadata is missing, the Personnel node may be probable, but the Open Issues node can still require review depending on the missing-field policy.
- If client and intended-user facts conflict, the Client/User node remains needs-review and the graph should not be treated as fully ready.

## Relationship to Knowledge Objects

The Memory Graph must be built from Knowledge Objects, not raw extraction candidates. Knowledge Object Builder V1 decides whether each object candidate is ready, probable, needs-review, or blocked. The Memory Graph preserves that status instead of hiding it.

```text
Verified Facts
-> Knowledge Object candidates
-> Memory Graph nodes
-> Memory Graph relationships
```

## Relationship to Property Passport

Property Passport is the operator-facing view of trusted property knowledge. The Memory Graph is the connection layer behind that view.

Property Passport V1 includes a synthetic Memory Graph Preview showing:

- Node count.
- Relationship count.
- Graph readiness.
- Relationship chips.
- Unresolved relationship warnings.
- A plain-language memory summary.

The preview is synthetic and read-only. It does not load ignored local graph outputs into the browser.

## Relationship to Insight Engine

The Insight Engine should eventually reason over graph-connected knowledge rather than isolated facts. For example:

- Repeated reports on the same property can reveal stable or changing assumptions.
- Client/user relationships can affect report reliance context.
- Personnel and reviewer history can support accountability and review routing.
- Open Issues can prevent insights from being presented as high-confidence.

No Insight Engine behavior is implemented by Memory Graph Prototype V1.

## Future Historical Timeline Support

Future graph versions should support time-aware memory:

- Effective dates.
- Report dates.
- Inspection dates.
- Review timestamps.
- Superseded facts and objects.
- Prior and current values.
- Multi-report property histories.

Timeline support should preserve the difference between a fact that was true at an effective date and a fact that is current today.

## Future Multi-Report Property Memory

Future graph versions should merge report packages that refer to the same property when verified identity rules support that merge. Until then, V1 keeps each graph local to one report package.

Future merge rules should consider:

- Verified property identity.
- Address normalization.
- Parcel and legal identifiers.
- Report effective date.
- Conflicting evidence.
- Operator review.

## Future Direct-Upload Workfile Discipline

Future direct-upload workflows should feed the same path:

```text
Workfile material
-> Candidate Facts
-> Verified Facts
-> Knowledge Objects
-> Memory Graph
```

Direct uploads should preserve final reports, engagement letters, source documents, maps, photos, rent rolls, comparable data, reviewer notes, and revision history as traceable context. The Memory Graph should connect these materials only after verification and promotion rules are satisfied.

## Guardrail

Memory Graph Prototype V1 is a local/synthetic architecture and prototype layer only. It does not authorize production persistence, production graph databases, Supabase schema changes, backend APIs, AI calls, OCR, embeddings, vector search, source-document parsing, real report ingestion, or uploads.
