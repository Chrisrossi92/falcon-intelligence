# Falcon Property Passport

The Property Passport is the operator-facing record of what Falcon Intelligence knows about a property or report package. It is not a document viewer. It is a trusted property knowledge surface built from Verified Facts.

Property Passport V1 is preview-only. It uses committed synthetic verified-fact fixtures in the frontend and does not load real ignored extraction, verification, report, client, or workfile outputs.

## Purpose

The Passport helps an operator answer:

```text
What is this property?
What does Falcon trust?
What is uncertain?
What needs review?
What can become knowledge?
```

## Relationship to Verified Facts

The Passport sits after the Verification Engine:

```text
Historical Intake
-> Historical Knowledge Extraction
-> Verification Engine
-> Verified Facts
-> Property Passport
-> Knowledge Object Builder
-> Memory Graph Prototype
```

Candidate metadata should not appear as trusted knowledge until the Verification Engine creates a Verified Fact ledger. The Passport displays the ledger in an operator-friendly form:

- Identity fields.
- Verification statuses.
- Confidence labels.
- Supporting evidence references.
- Conflicting and missing fields.
- Readiness for future Knowledge Object creation.

## Passport V1 Preview

Passport V1 currently shows:

- Property identity.
- Verified/probable/conflicting/missing/needs-review fact counts.
- Compact trust and confidence badges.
- Evidence references with source labels, methods, and source hints.
- Knowledge Object Preview rows for Property, Report, Client/User, Personnel, and Open Issues candidates.
- Memory Graph Preview counts, readiness, relationship chips, and unresolved warnings.
- A plain-English summary of what Falcon knows so far.
- Readiness state for future Knowledge Object creation.

The preview intentionally avoids source document text, OCR output, AI analysis, embeddings, production uploads, backend APIs, Supabase schemas, and Memory Graph implementation.

## Relationship to the Knowledge Model

The Passport is not itself the full Knowledge Model. It is the operator preview that explains which Verified Facts are ready to become future canonical objects such as:

- Property.
- Report.
- Client.
- Appraiser.
- Reviewer.
- Inspection.
- Certification.
- Extraordinary assumptions.
- Hypothetical conditions.

Knowledge Object creation should consume Verified Facts and their provenance, not raw extraction candidates. The current Passport preview shows synthetic Knowledge Object candidates only; it does not load ignored local outputs or create durable records.

## Relationship to the Intelligence Engine

The Passport makes the lower layers of the Intelligence Engine visible:

```text
Documents
-> Facts
-> Knowledge
```

It does not generate insights, recommendations, or actions by itself. Those later layers should rely on Passport-backed Verified Facts and future Knowledge Objects.

## Relationship to the Future Memory Graph

The Memory Graph should connect properties, reports, clients, appraisers, reviewers, open issues, comps, markets, evidence, and review history. The Passport V1 preview shows synthetic graph counts and relationship chips only; it does not load ignored graph outputs or create production graph records.

The Passport should eventually become the human-readable view into Memory Graph knowledge, but only after Verified Facts are promoted into durable Knowledge Objects.

## Future Direct-Upload Workfile Discipline

Future direct uploads should preserve complete appraisal workfile context so the Passport can remain auditable:

- Final report.
- Engagement letter.
- Source documents.
- Rent roll and financials.
- Maps.
- Photos.
- Comparable data.
- Reviewer notes.
- Revision history.

This discipline avoids ad hoc knowledge records and keeps future Passport views traceable.

## Current Guardrail

Property Passport V1 is a frontend preview using synthetic/local model fixtures. It is not production data, not a backend API, not a report viewer, not the Memory Graph, and not a Knowledge Object creation workflow.
