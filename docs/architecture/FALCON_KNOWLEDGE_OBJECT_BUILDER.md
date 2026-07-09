# Falcon Knowledge Object Builder V1

The Knowledge Object Builder is the local, deterministic bridge from Verified Facts into durable knowledge candidates. It does not create production schemas, APIs, uploads, Memory Graph nodes, embeddings, OCR output, AI output, or report ingestion.

## Position in the Intelligence Engine

```text
Documents
-> Candidate Facts
-> Verified Facts
-> Knowledge Object Candidates
-> Memory Graph Prototype
-> Insights
-> Recommendations
-> Actions
```

The builder consumes Verification Engine output only. It does not inspect source report bodies or decide facts directly from documents.

## Purpose

The builder answers:

- Which Verified Facts can form stable appraisal knowledge.
- Which future objects can be promoted safely.
- Which missing or conflicting fields must remain visible to an operator.
- Which facts should later become Property, Report, Client/User, Personnel, or Open Issues records.

## V1 Object Candidates

### Property Object

Purpose: identify the subject or related property record.

Required V1 fields: property address.

Promotion rule: ready when property address is verified or probable and not conflicting. Blocked when property address conflicts.

### Report Object

Purpose: represent the appraisal report package and effective-dated assignment context.

Required V1 fields: report type and effective date.

Promotion rule: ready when report type and effective date are verified or probable and not conflicting.

### Client/User Object

Purpose: preserve who requested the work and who may rely on it.

Required V1 fields: client and intended user.

Promotion rule: ready when both are verified or probable. Conflicts remain needs-review so an operator can resolve client/user ambiguity without blocking unrelated object candidates.

### Personnel Object

Purpose: preserve appraiser and reviewer attribution.

Required V1 fields: appraiser and reviewer.

Promotion rule: probable when appraiser is known but reviewer is missing. Blocked when personnel fields conflict.

### Open Issues Object

Purpose: preserve conflicts, missing critical fields, and low-confidence review items as first-class knowledge work.

Promotion rule: ready when no V1 issues exist, needs-review when missing or low-confidence issues exist, and blocked when conflicts exist.

## Candidate Shape

Each candidate records:

- Object type.
- Stable key and local object id.
- Display label.
- Source Verified Facts.
- Confidence label.
- Readiness state.
- Missing required fields.
- Conflicting fields.
- Notes.
- Timestamp.

This shape is local and preview-oriented. It is not a production schema contract.

## Readiness States

- `ready`: sufficient verified/probable facts exist for future promotion.
- `probable`: usable partial knowledge exists, but a non-critical missing field should be reviewed.
- `needs_review`: operator review is required before promotion.
- `blocked`: conflicting critical facts prevent promotion.

## Relationship to Property Passport

Property Passport V1 displays the same Verified Facts an operator sees. Its Knowledge Objects Preview shows how those facts would become object candidates:

```text
Verified Fact ledger
-> Knowledge Object candidate
-> Readiness badge
-> Missing/conflicting field cues
```

The preview is synthetic and read-only. It does not load ignored local outputs or real client/report data.

## Relationship to Future Memory Graph

The Memory Graph should accept only Knowledge Objects with traceable Verified Facts. This builder defines the promotion discipline before relationships are created.

Memory Graph Prototype V1 preserves:

- Stable object identity.
- Source fact lineage.
- Evidence and conflict visibility through object readiness.
- Operator review status through needs-review and blocked states.
- Object relationships between Property, Report, Client/User, Personnel, and Open Issues.

## Guardrails

Knowledge Object Builder V1 is local architecture and preview infrastructure only. It does not authorize real extraction, AI calls, OCR, embeddings, vector storage, OneDrive integration, Supabase schema changes, backend APIs, Memory Graph implementation, production upload, or source-document parsing.
