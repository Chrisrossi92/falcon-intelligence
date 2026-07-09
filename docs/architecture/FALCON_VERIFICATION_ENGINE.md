# Falcon Verification Engine

This document defines the permanent Verification Engine for Falcon Intelligence. The Verification Engine promotes candidate metadata into explainable Verified Facts using deterministic rules.

It does not authorize OCR, AI extraction, embeddings, vector databases, Supabase schemas, production APIs, uploads, source-file modification, Memory Graph implementation, Knowledge Graph implementation, or production fact storage.

## Core Principle

Falcon Intelligence distinguishes:

```text
Candidate
-> Verified Fact
-> Knowledge Object
```

A candidate may be correct. A Verified Fact is trusted because Falcon can explain why it believes the value is true.

## Why Candidates Are Not Facts

Historical Knowledge Extraction produces candidate metadata from deterministic labels and phrases. Those candidates are useful but still untrusted because:

- A label can appear more than once.
- A report can contain historical references or conflicting names.
- A filename can disagree with report text.
- Searchable text can be incomplete.
- A missing value must not be fabricated.

The Verification Engine is the boundary where Falcon decides whether a candidate can become a fact, should remain probable, is missing, or requires review.

## Verified Fact Model

Each Verified Fact ledger contains:

- Field name.
- Verified value.
- Verification status.
- Confidence.
- Supporting evidence.
- Conflicting evidence.
- Verification method.
- Verification timestamp.
- Notes.
- Source references.

Source references are short provenance handles, not copied report text.

## Verification Statuses

| Status | Meaning |
| --- | --- |
| Verified | Multiple independent evidence references agree after deterministic normalization. |
| Probable | A candidate exists, but independent agreement is not yet available. |
| Conflicting | Candidate values disagree after normalization. |
| Missing | No candidate value exists. |
| Rejected | A candidate was rejected by a deterministic rule. |
| Needs review | Evidence exists but is too weak for promotion. |

## Deterministic Rule Engine

The Phase 1 rule engine supports:

- Agreement rules: independent sources that normalize to the same value become verified with high confidence.
- Conflict rules: disagreeing values are retained as conflicting evidence; Falcon does not guess.
- Missing rules: absent values remain missing; Falcon does not fabricate.
- Normalization rules: whitespace, capitalization, punctuation, ampersands, and common street suffixes are normalized before comparison.
- Single-source rules: one supported value may be probable, not fully verified.

## Verification Ledger

Every field produces a ledger entry, even when missing. A ledger answers:

```text
What value does Falcon believe?
Why?
Which evidence supports it?
Which evidence conflicts?
When was it verified?
What rule was used?
```

The ledger is intentionally small. It stores values and source references, not long report excerpts.

## Relationship to Historical Knowledge Extraction

Historical Knowledge Extraction answers:

```text
What candidate metadata can be deterministically found?
```

The Verification Engine answers:

```text
What is Falcon willing to believe, and why?
```

The verifier consumes the ignored historical knowledge output and produces ignored local verification outputs under:

```text
data/verification/
```

Expected local files:

```text
verification-report.json
verification-summary.md
```

## Relationship to Knowledge Object Builder V1

The Knowledge Object Builder consumes Verification Engine output and groups Verified Facts into local object candidates:

```text
Verified Facts
-> Property / Report / Client-User / Personnel / Open Issues candidates
-> Future Memory Graph promotion review
```

The builder does not verify facts itself. It preserves the Verification Engine's evidence, confidence, and conflict boundaries by marking object candidates as ready, probable, needs-review, or blocked.

## Relationship to the Knowledge Model

Verified Facts are the input boundary for future Knowledge Objects. A Property, Report, Client, Appraiser, or Market object should not be built directly from raw extraction candidates.

Future Knowledge Model creation should require:

- Verified value.
- Verification status.
- Confidence.
- Supporting evidence.
- Source references.
- Audit trail.

## Relationship to Future AI Extraction

Future AI extraction may produce candidates, but AI candidates should still enter the same verification path. AI should not bypass deterministic ledger rules.

Future evidence sources may include:

- Engagement letters.
- Previous reports.
- Future direct uploads.
- OCR output.
- AI extraction candidates.
- Reviewer confirmations.

These are future inputs only. They are not implemented in Phase 1.

## Relationship to the Future Memory Graph

The Memory Graph should be built from Verified Facts and Knowledge Objects, not raw candidates. This sprint does not create Memory Graph nodes, edges, embeddings, vector indexes, or graph storage.

## Current Guardrail

The Phase 1 Verification Engine is local, deterministic, and explanatory. It promotes only simple metadata candidates into local Verified Fact ledgers. It does not perform appraisal analysis, create production records, or decide business actions.
