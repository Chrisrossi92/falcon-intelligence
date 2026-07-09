# Falcon Confidence Model

This document defines the trust architecture for Falcon Intelligence. It is documentation-only and does not implement scoring, model confidence, extraction confidence, OCR, embeddings, report ingestion, production APIs, OneDrive integration, Supabase changes, source-document preview, or real report processing.

Confidence in Falcon Intelligence means trust context. It is not a single magic score and it is not a valuation reliability guarantee.

## Confidence Principles

- Confidence must be multi-dimensional.
- Evidence should be visible before certainty is implied.
- Conflicts should lower trust or require review.
- Freshness should be explicit.
- Verification state should be separate from system-generated confidence.
- Explainability should be available for every future insight and recommendation.
- Confidence language must preserve appraiser and reviewer judgment.

## Trust Envelope

Every future fact, knowledge object, insight, recommendation, and action should eventually carry a trust envelope appropriate to its layer.

| Dimension | Meaning | Applies to |
| --- | --- | --- |
| Confidence | Overall trust context or display label, if policy permits a combined indicator. | Facts, knowledge, insights, recommendations. |
| Supporting evidence | Evidence references that support the claim or recommendation. | All layers except raw documents. |
| Conflicting evidence | Known conflicts, mismatches, superseded records, or unresolved discrepancies. | Facts, knowledge, insights, recommendations. |
| Freshness | Whether the underlying evidence and verification remain current enough for the use case. | Facts, knowledge, comparables, market indicators, recommendations. |
| Verification state | Human review lifecycle status. | Facts, knowledge objects, recommendations requiring approval. |
| Explainability | Product-level reasoning that describes why the system surfaced the item. | Insights and recommendations, with links back to facts and evidence. |
| Source quality | Appropriateness and reliability of source evidence for the claim. | Facts and derived knowledge. |
| Permission state | Whether the current user can view, open, verify, or act on the item. | Evidence, facts, knowledge, recommendations, actions. |
| Audit state | Who created, reviewed, verified, rejected, superseded, or acted on the item. | Facts, knowledge, recommendations, actions. |

## Verification States

Canonical verification states should include:

| State | Meaning |
| --- | --- |
| Suggested | Proposed by user entry, metadata, future extraction, or controlled AI assistance. Not verified. |
| In Review | Being checked by an authorized person. |
| Verified | Accepted under firm policy by an authorized person. |
| Rejected | Reviewed and declined. |
| Needs More Evidence | Cannot be verified without stronger or additional support. |
| Conflict Review | Conflicting evidence or historical values require resolution. |
| Superseded | Replaced by newer verified knowledge. |
| Archived | Retained for audit or history, hidden from ordinary reuse. |
| Restricted | Validity or visibility limited by policy, role, client confidentiality, or source restrictions. |

Future UI should not collapse these into a vague "trusted" badge. Users need to know the lifecycle state.

## Evidence Support

Supporting evidence explains why a fact, knowledge object, insight, or recommendation exists.

Evidence support should eventually include:

- Evidence ID.
- Evidence type.
- Source object or document metadata.
- Source quality.
- Relevant date.
- Relationship to the claim.
- Access policy.
- Whether source preview is available.
- Verification notes.

Current repository rule: evidence remains metadata-only. Source-document preview, source text, OCR output, copied files, and content snippets are not authorized.

## Conflicting Evidence

Conflicting evidence should be modeled directly instead of hidden.

Conflict examples:

- Different GLA values for the same property.
- Different sale prices for the same transaction.
- Conflicting lease dates or rent terms.
- Market indicators from different date ranges.
- Report conditions that make two facts contextually different rather than simply inconsistent.

Conflict states:

| State | Meaning |
| --- | --- |
| No known conflict | No material conflict identified. |
| Possible conflict | A mismatch may matter and needs review. |
| Confirmed difference | Difference is valid because context differs. |
| Resolved | Conflict was reviewed and corrected or accepted. |
| Superseded | Older value replaced by newer verified knowledge. |

Insights and recommendations should disclose material conflicts and route them to review rather than silently choosing a value.

## Freshness

Freshness describes whether evidence or knowledge remains current enough for a particular workflow.

Freshness should consider:

- Effective date.
- Report date.
- Verification date.
- Source date.
- Stale-after policy.
- Market volatility.
- Property type.
- Evidence type.
- Whether the current use is review, search, comp reuse, market context, or report support.

Freshness states:

| State | Meaning |
| --- | --- |
| Current | Within policy for the intended use. |
| Aging | Approaching stale threshold or may need attention. |
| Stale | Past policy threshold for ordinary reuse. |
| Reverification Required | Must be checked before use. |
| Unknown | Missing dates or insufficient policy context. |

Freshness should influence recommendations. For example, stale knowledge may still be useful context, but should not be reused as verified support without reverification.

## Explainability

Explainability is the user's ability to understand why Falcon Intelligence surfaced an insight or recommendation.

An explainable insight should answer:

- What knowledge object is this about?
- Which facts support it?
- Which evidence supports those facts?
- Is there conflicting evidence?
- Is the information current?
- Has a human verified it?
- What action is recommended and why?

Explainability should be concise in the workspace and detailed in drill-down surfaces. It should avoid model jargon unless the user is in an admin or diagnostics context.

## Confidence Display

Confidence should appear as layered context:

| Surface | Display guidance |
| --- | --- |
| Insight cards | Show confidence label, verification state, freshness, and conflict warning if material. |
| Recommendation panel | Show why the step is recommended and what support or limitation exists. |
| Passport drawer | Show detailed confidence dimensions and evidence summaries. |
| Supporting Evidence drawer | Show evidence source, access state, and support relationship. |
| Review History drawer | Show human actions, timestamps, and decisions. |
| Map/table | Show compact badges only; avoid heavy color or AI-style certainty visuals. |

Possible display labels may include high, medium, low, needs review, stale, conflicting, verified, restricted, or unavailable. Final labels require product and policy approval. This document does not define scoring thresholds.

## Scoring Boundary

This sprint does not implement scoring.

Future scoring, if approved, must follow these rules:

- It must be explainable.
- It must be separate from verification state.
- It must not override appraiser or reviewer judgment.
- It must expose source, conflict, and freshness limitations.
- It must be tenant-scoped.
- It must be auditable when used for workflow routing.
- It must not imply valuation certainty.

## Relationship to Existing Provenance Model

`docs/data-confidence-provenance-model.md` remains the detailed current design for data passports, evidence links, confidence dimensions, permissions, and historical comparable workflow.

This document adds the canonical cross-layer trust architecture:

```text
Facts
-> Knowledge
-> Insights
-> Recommendations
-> Actions
```

The existing data passport concept should be interpreted as one visible trust container inside this broader Confidence Model.

## Current Guardrail

This model defines trust architecture only. It does not add fields, tables, APIs, scoring, extraction, source access, real report handling, or production confidence computation. Future work must define separate implementation contracts and approval gates before any scoring or source-based processing exists.
