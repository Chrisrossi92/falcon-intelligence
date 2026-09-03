# Falcon Local Intake Review and Assignment/Property Brief V1

Local Intake Review is the first appraisal-production workflow over the canonical Assignment Intelligence Record (AIR) V1. It turns deterministic extracted candidates into explicit appraiser decisions, rebuilds readiness, and produces a compact Assignment/Property Brief without creating a second assignment or review-state model.

This implementation is synthetic and local-first. It is not a production API, database, source-document viewer, report writer, valuation engine, or live Project Falcon integration.

## Product Position

Project Falcon continues to own orders, users, permissions, workflow, delivery, and client-facing operations. Falcon Intelligence owns evidence, candidate observations, provenance, appraiser review events, canonical facts and revisions, conflicts, AIR readiness, and the derived brief.

```text
Synthetic searchable document text
-> historical extraction candidates
-> deterministic machine assessment
-> immutable AIR evidence/candidate identities
-> explicit appraiser review events
-> canonical AIR rebuild and readiness
-> Assignment/Property Brief V1
-> deterministic local JSON/Markdown exports
```

## Verified Starting Connections

| Concern | Existing authority | Local Intake Review use |
| --- | --- | --- |
| PDF/DOCX extraction | `historical_knowledge.py` | Reuses `PageText`, structured `MetadataCandidate` values, and source hints. |
| Deterministic verification | `verification_engine.py` | Reuses normalization, agreement/conflict status, confidence, and evidence collection. Machine verification does not promote a fact. |
| Evidence and provenance | `assignment_intelligence_record.py` | Reuses immutable `SourceReference`, `EvidenceReference`, locators, extractor identity, quality, and candidate links. |
| Report Field Registry | `report_registry.py` | Reuses appraisal labels and dot-notation conventions where compatible. Registry approval/lock status is not used as review state. |
| AIR V1 | `assignment_intelligence_record.py` | Remains the only canonical assignment intelligence and decision record. |
| Existing correction preview | `correction_audit.py` and React Passport panel | Supplies presentation patterns only. Its narrower demo model is not used as workflow state. |
| Existing Intelligence Workspace | `frontend/src/workspace/` | Remains a fixture-only map/passport/evidence preview. The new focused intake workspace reuses restrained cards, drawers, status, filters, and accessible native controls. |
| Local outputs | existing `save_*_outputs` helpers and ignored directories | Brief export adds explicit destination validation before writing AIR JSON, brief JSON, or Markdown. |

## Domain Decisions

`LocalIntakeReviewSession` is an application-service input bundle, not a second canonical record. It contains the immutable candidate/evidence bundles plus AIR-native `ReviewEvent` and `AppraiserFactInput` values required to deterministically rebuild AIR.

Supported review operations are:

- Accept: appends `candidate_verified` and promotes a verified current fact.
- Correct: appends `candidate_corrected`, retains the original candidate/evidence, and creates a corrected fact revision.
- Reject: appends `candidate_rejected`; the candidate, evidence, and reason remain. A rejection removes a current fact only when that fact came from the rejected candidate.
- Defer: appends `candidate_deferred`; it creates no fact, does not count as verification, and produces a nonblocking or policy-derived readiness issue.
- Resolve conflict: appends one explicit accept/correct event for the selected candidate and rejection events for every competitor, all with the resolution reason. The AIR conflict remains visible with `resolved` state and resolution event IDs.
- Add fact: appends an `appraiser_fact_entered` event and an `appraiser_entered` fact with actor, time, reason, optional evidence, and explicit supersession when applicable.

Corrections and later replacements are additive. Candidate and evidence IDs do not change. Conflicts remain unresolved until exactly one competing candidate is accepted or corrected and all others are explicitly rejected.

## Review Workspace Adapter

`build_local_intake_review_workspace` creates the versioned `local_intake_review_workspace` projection. It includes:

- AIR identity and complete deterministic AIR payload;
- assignment overview from current facts;
- topic-grouped candidates with inline source, locator, method, confidence, quality, state, conflict IDs, and actions;
- review progress, missing critical information, conflicts, readiness, and blockers;
- Assignment/Property Brief V1 and exact Markdown;
- supported local export format names.

The committed synthetic snapshot at `tests/fixtures/synthetic_intake_review/local-intake-review-workspace-v1.json` is generated from the Python workflow and checked for exact equivalence in backend tests. React imports this versioned projection; it is not a disconnected hand-authored mock. Browser actions exercise the event vocabulary locally for UI proof, while the Python application service remains the authoritative mutation/rebuild boundary until a later approved local API or persistence layer exists.

## Candidate Topics

Candidates are grouped from AIR field keys into practical appraisal topics:

- assignment and engagement;
- client and intended users;
- intended use and appraisal purpose;
- important dates;
- subject identity and location;
- property characteristics;
- ownership and transaction history;
- zoning, taxes, and legal information;
- income and occupancy;
- contacts and inspection;
- comparables and market references;
- signing and review information;
- unresolved or unclassified items.

No frontend-only field dictionary is introduced. Unknown keys remain visible under the unresolved/unclassified topic.

## Assignment/Property Brief V1

`build_assignment_property_brief` reads only current AIR facts, evidence, references, conclusions, and readiness. Absent facts are omitted rather than inferred.

The brief contains:

- assignment synopsis and contacts;
- subject synopsis and ownership references;
- issues requiring attention;
- readiness by appraisal area;
- evidence citations from fact ID to evidence ID, source, locator, method, confidence, quality, and freshness;
- comparable and market leads marked with their actual reference/selection state;
- explicit professional-boundary language;
- appraiser-authored professional conclusions only when AIR already contains them.

Every shown fact is labeled as a verified fact, corrected fact, appraiser-entered fact, or another explicit AIR fact. Unresolved candidates are issues, not facts. Readiness never becomes a professional conclusion. Brief V1 does not generate value, highest and best use, comparable selection, adjustments, capitalization rates, or appraisal narrative.

## Deterministic Export and Safety

`export_assignment_property_brief` writes:

- `assignment-intelligence-record-v1.json`;
- `assignment-property-brief-v1.json`;
- `assignment-property-brief-v1.md`.

The caller must supply an output directory. Destinations outside the repository are allowed. Destinations inside the repository are allowed only under ignored `data/`, `exports/`, `local-data/`, or `local_data/` roots. Tracked source, documentation, frontend, and test paths are rejected. The exporter includes AIR schema/record versions and Brief V1 format version, preserves evidence references, and marks unresolved information through readiness issues.

Runtime output is not committed. Extracted text, OCR output, source documents, databases, and embeddings remain ignored and outside this workflow.

## Synthetic Vertical Proof

`build_synthetic_local_intake_review_proof` uses two code-only synthetic documents and exercises:

- 20 extracted candidates across seven populated topics;
- accepted, corrected, rejected, and deferred states;
- appraiser-entered assignment and property facts;
- a client conflict explicitly resolved by accept/reject events;
- intended-use and report-format conflicts deliberately left unresolved;
- missing critical appraisal purpose;
- evidence locators, extraction methods, confidence, and source quality;
- deterministic AIR and brief rebuilds;
- JSON and Markdown export and AIR round trip;
- the exact versioned projection consumed by React.

## Deferred Production Decisions

- Durable review-session persistence, concurrency, and event locking.
- Live Project Falcon assignment, actor, permission, and audit integration.
- A local HTTP/RPC adapter replacing the committed synthetic projection.
- Real-document pilot authorization and real extracted facts.
- Source-document preview and evidence opening.
- Firm/client/property-type readiness policy selection.
- Production export retention and access controls.

These remain behind existing readiness gates.
