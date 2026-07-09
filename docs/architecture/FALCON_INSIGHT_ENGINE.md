# Falcon Insight Engine

This document defines how Falcon Intelligence should create insights, recommendations, and actions from verified knowledge. It is documentation-only and does not authorize AI extraction, report ingestion, OCR, embeddings, OneDrive integration, source-document preview, production APIs, Supabase changes, or real report processing.

The Insight Engine is the reasoning layer above the Knowledge Model. It interprets verified facts and knowledge objects, but it does not replace appraiser or reviewer judgment.

## Canonical Distinctions

Falcon Intelligence must keep these concepts separate:

| Concept | Definition | Product behavior |
| --- | --- | --- |
| Fact | An atomic statement with evidence and verification state. | Display as a checked or checkable claim. |
| Knowledge | A structured object or relationship composed from verified facts. | Display as institutional context such as Property, Comparable, Market, or Report knowledge. |
| Insight | An interpretation, pattern, risk, gap, or implication derived from knowledge. | Display with explanation, evidence, and confidence context. |
| Recommendation | A suggested next review step based on an insight. | Display as optional workflow guidance. |
| Action | A user-controlled operation that applies or investigates a recommendation. | Require permissions, context preservation, and audit where appropriate. |

The system may eventually use AI assistance, but the product contract is not "AI says an answer." The contract is "Falcon shows what the firm knows, why it matters, what to review next, and how to act."

## Insight Generation Flow

The reusable flow is:

```text
Verified Facts
-> Knowledge Objects
-> Context Assembly
-> Insight Candidate
-> Confidence Review
-> Recommendation Candidate
-> Operator Action
```

### 1. Verified Facts

Inputs are facts with source evidence, verification state, freshness, conflicts, and audit history.

Rule: unverified facts may be visible as suggestions but should not drive firm-searchable knowledge or high-impact recommendations.

### 2. Knowledge Objects

Facts are composed into canonical objects such as Property, Comparable, Sale, Lease, Market, Report, Adjustment, or Narrative.

Rule: the object model controls meaning. Future AI features should not invent ad hoc object categories when a canonical object exists.

### 3. Context Assembly

The engine assembles relevant context:

- Current assignment or workspace selection.
- Property, market, and report context.
- Verification and reviewer state.
- Freshness and stale policy.
- Conflicting or superseded facts.
- Permission context.
- Assumptions and hypothetical conditions.

Rule: insights should be contextual. The same fact may support different recommendations depending on assignment type, market, effective date, role, and policy.

### 4. Insight Candidate

An insight candidate identifies a meaningful pattern, risk, gap, or relationship.

Insight categories:

| Category | Purpose |
| --- | --- |
| Consistency insight | Identifies whether related facts agree or conflict. |
| Freshness insight | Identifies whether knowledge may be stale or needs reverification. |
| Completeness insight | Identifies missing facts, evidence, or verification needed for reuse. |
| Relationship insight | Identifies related properties, comps, reports, markets, or evidence. |
| Workflow insight | Identifies a review queue, approval need, or next workflow state. |
| Risk insight | Identifies sensitive, ambiguous, conflicting, stale, or policy-limited knowledge. |
| Opportunity insight | Identifies relevant prior work, reusable verified context, or helpful market knowledge. |

Rule: an insight must name the knowledge it is based on and the reason it matters.

### 5. Confidence Review

Each insight candidate should be evaluated against the trust model:

- Supporting evidence.
- Conflicting evidence.
- Freshness.
- Verification state.
- Source quality.
- Explainability.
- Permission and policy constraints.

Rule: confidence is not a production score in this sprint. The architecture requires a trust envelope, not an implemented scoring system.

### 6. Recommendation Candidate

A recommendation translates an insight into a suggested next step.

Recommendation types:

| Type | Example intent |
| --- | --- |
| Inspect | Open supporting evidence, review a Passport, or inspect a related object. |
| Verify | Start fact verification, compare conflicts, or confirm source quality. |
| Reverify | Refresh stale evidence or require updated confirmation. |
| Escalate | Request reviewer approval or admin policy review. |
| Compare | Compare related properties, sales, leases, or report records. |
| Defer | Avoid reuse until verification, evidence, or freshness improves. |
| Navigate | Open a relevant workspace section or future report area. |

Rule: recommendations should explain why they are offered and what evidence or knowledge supports them.

### 7. Operator Action

Actions are concrete UI or workflow operations selected by a user.

Action rules:

- Respect role permissions.
- Preserve workspace context.
- Avoid automatic valuation decisions.
- Create audit events for meaningful review, verification, reuse, override, or rejection.
- Make unavailable actions clear without exposing restricted evidence.

## Reusable Insight Envelope

Every future insight should eventually fit this conceptual envelope:

| Field | Purpose |
| --- | --- |
| Insight ID | Stable reference for UI, audit, and feedback. |
| Tenant ID | Tenant isolation. |
| Subject object | The knowledge object the insight is about. |
| Insight category | Consistency, freshness, completeness, relationship, workflow, risk, or opportunity. |
| Claim | Short statement of what the insight says. |
| Why it matters | Product-level explanation of workflow relevance. |
| Supporting knowledge | Facts and objects supporting the insight. |
| Supporting evidence | Evidence references, metadata-only until approved otherwise. |
| Conflicting evidence | Known conflicts or unresolved issues. |
| Confidence context | Trust dimensions from the Confidence Model. |
| Recommendation | Suggested next step. |
| Available actions | Permission-aware operator actions. |
| Status | Draft, visible, dismissed, acted on, superseded, or archived. |
| Audit references | Review and action trail. |

This envelope is not a schema implementation. It is the architecture shape future schemas and UI contracts should align with.

## Recommendation Rules

Recommendations should be:

- Specific enough to act on.
- Conservative in valuation language.
- Tied to evidence and knowledge.
- Role- and permission-aware.
- Clear about stale, incomplete, or conflicting support.
- Easy to dismiss or defer with audit when appropriate.

Recommendations should not:

- State final value conclusions.
- Automatically select comparables.
- Hide uncertainty.
- Present source-document access when it is not approved.
- Promote unverified suggestions as firm knowledge.
- Imply that AI has reviewer authority.

## Workspace Integration

The current Intelligence Workspace preview should eventually show Insight Engine output in these places:

| Surface | Future role |
| --- | --- |
| Knowledge Summary | Show the highest-priority selected-object insight and why it matters. |
| Passport drawer | Show fact-level insight context, conflicts, freshness, and relationship explanations. |
| Supporting Evidence drawer | Show supporting and conflicting evidence references. |
| Review History drawer | Show which insights or recommendations were acted on, dismissed, escalated, or superseded. |
| Recommendation panel | Show prioritized next steps for the selected property, comp, report, or market context. |
| Map and layers | Show relationship, freshness, stale, conflict, and review-status signals without turning the map into an AI dashboard. |
| Table rows | Show compact insight and recommendation indicators for professional scanning. |

The first workspace expression should be modest: insight cards, recommendation panel, confidence badges, evidence drill-down, and relationship links. Full automation is out of scope.

### Current Synthetic Preview

The current React workspace includes a frontend-only Insight Layer Preview that demonstrates this first expression against committed synthetic data.

It includes:

- Three to five compact insight cards for the selected synthetic record.
- A recommendation panel with appraisal-specific next-step language.
- Synthetic trust badges for high confidence, needs verification, conflicting evidence, and stale evidence.
- A metadata-only evidence drill-down preview.
- A Facts to Knowledge to Insight to Recommendation relationship chain.

The preview data lives in the frontend workspace data layer and is intentionally not a production schema, backend contract, AI output, extraction target, or persisted insight store. It exists to make the Intelligence Engine feel tangible inside the current workspace while keeping implementation gates closed.

## Feedback and Learning Boundaries

Future feedback loops may record whether users opened, dismissed, accepted, edited, or rejected recommendations.

Rules:

- Feedback should improve product workflow, not silently alter firm knowledge.
- User action does not verify a fact unless the action is explicitly a verification action.
- Rejected recommendations should remain auditable when they affected review or reuse.
- Cross-tenant learning must not use firm-owned knowledge or confidential source content.

## Current Guardrail

This document defines the reusable insight architecture only. It does not implement reasoning, scoring, AI calls, extraction, embeddings, source access, production workflows, or data pipelines. Future implementation must build on verified knowledge objects and the confidence model before surfacing recommendations.
