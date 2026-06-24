# Session Handoff and Roadmap Checkpoint

This checkpoint summarizes the current Falcon Intelligence prototype state and recommended next direction. It is documentation-only and does not authorize real data access, OneDrive access, report parsing, extraction, OCR, embeddings, or ingestion.

## Product Vision

Falcon Intelligence is a local-first appraisal firm knowledge base prototype. The near-term product direction is an internal-only "Firm Intelligence Found" experience that helps Project Falcon surface prior verified firm knowledge while an order is being created, reviewed, or worked.

The product should help appraisers and reviewers answer:

- Have we seen this subject property before?
- Do we have relevant prior assignments, sale comps, lease comps, or market indicators?
- Why should a surfaced fact be trusted?
- Where is the provenance, evidence, and audit trail?

Falcon Intelligence is assistive. It must not produce automatic valuation conclusions or automatic report language without appraiser review.

## Safety and Data Boundaries

Current non-negotiable boundaries:

- Use committed synthetic fixtures only.
- Do not add real appraisal reports, client files, source documents, OneDrive exports, extracted text, OCR output, embeddings, vector stores, databases, PDFs, DOCX, XLSX, CSV, TSV, or TXT exports.
- Do not read report contents.
- Do not inspect unrelated OneDrive files.
- Do not add extraction, OCR, embedding, retrieval, or report parsing code.
- Keep all current workflows metadata-only and local.

Explicit warning: do not add real report extraction yet. Metadata-only real-data scans are allowed, but report content extraction, OCR, embeddings, and source-document preview are blocked until `docs/real-data-production-readiness-gate.md` passes.

## Implemented So Far

Core scaffold:

- Local-first package scaffold in `src/falcon_intel`.
- Safety and architecture documentation under `docs/`.
- Development setup with `pytest` as a dev dependency.
- GitHub Actions validation workflow.

Synthetic metadata workflows:

- Metadata scanner, manifest creation, manifest search, assignment discovery, and assignment profile generation.
- Committed synthetic sample fixture tree under `tests/fixtures/synthetic_sample_data/`.
- Synthetic manifests and assignment profiles for industrial, retail, office, purchase, lease-heavy, and work-in-progress assignments.

Firm Intelligence card prototype:

- Synthetic verified intelligence fixture at `tests/fixtures/synthetic_verified_intelligence/verified-intelligence.json`.
- Synthetic matcher for fake Falcon order payloads.
- CLI preview command for the Firm Intelligence Found card.
- Stable UI-facing v1 card schema with snapshot fixture at `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json`.
- Local Falcon-style card contract boundary for synthetic card responses.

Trust, provenance, and audit scaffolding:

- Stable policy codes for match categories, warning codes, action codes, and audit events.
- Local audit event builders for card view, evidence open, match select/reject, and justification.
- Historical comparable justification model and reusable narrative draft.
- Evidence link model for future "open evidence" behavior.
- Data passport model for full provenance detail.
- Compact passport summaries on top match cards.
- Synthetic data passport detail fixture at `tests/fixtures/synthetic_data_passports/data-passports.json`.
- Local passport detail lookup from `tenant_id` and `passport_id`.
- Falcon-style passport detail contract boundary with suggested `opened_evidence` audit event.
- Versioned synthetic passport detail drawer UI contract snapshot at `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json`.
- Falcon-style evidence-open contract boundary that validates an evidence link belongs to a passport and returns a metadata-only summary plus suggested audit event.
- Synthetic/local permission policy scaffold for internal role and evidence visibility decisions.
- End-to-end synthetic workflow that builds a card, opens passport detail, checks permissions, opens evidence, and returns suggested audit payloads.
- Documentation-only real data production readiness gate at `docs/real-data-production-readiness-gate.md`.
- Documentation-only Falcon UI integration notes at `docs/falcon-ui-integration-notes.md`.
- Lightweight schema version registry at `docs/schema-version-registry.md` and `src/falcon_intel/schema_registry.py`.

## Current Validation Status

Current local validation is passing.

Run full validation:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
PYTHONPATH=src python3 scripts/smoke_synthetic_fixtures.py
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_schema.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_snapshot.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_cli.py
PYTHONPATH=src python3 scripts/smoke_falcon_api_contract.py
PYTHONPATH=src python3 scripts/smoke_match_audit.py
PYTHONPATH=src python3 scripts/smoke_historical_comp.py
PYTHONPATH=src python3 scripts/smoke_evidence_links.py
PYTHONPATH=src python3 scripts/smoke_data_passport.py
PYTHONPATH=src python3 scripts/smoke_data_passport_lookup.py
PYTHONPATH=src python3 scripts/smoke_falcon_passport_contract.py
PYTHONPATH=src python3 scripts/smoke_passport_detail_drawer.py
PYTHONPATH=src python3 scripts/smoke_falcon_evidence_contract.py
PYTHONPATH=src python3 scripts/smoke_schema_registry.py
PYTHONPATH=src python3 scripts/smoke_permission_policy.py
PYTHONPATH=src python3 scripts/smoke_synthetic_workflow.py
PYTHONPATH=src python3 -m pytest
```

CI runs the same synthetic-only core checks on push and pull request.

## Synthetic and Local Only

The following remain synthetic/local only:

- Matcher scoring and ranking.
- Verified intelligence records.
- Data passport details.
- Evidence links.
- Audit events.
- Falcon card, passport, and evidence-open contract boundaries.
- Historical comparable justification narratives.
- UI card and passport detail drawer snapshots.
- Permission decisions.

None of these are production APIs, database queries, permission checks, source-document viewers, report readers, or extraction systems.

## Project Falcon Tie-In

Falcon Intelligence currently supports Project Falcon integration through local contract helpers:

- `build_falcon_intelligence_card_response`: accepts a Falcon-style synthetic order payload and returns the v1 Firm Intelligence Found card.
- `build_falcon_passport_detail_response`: accepts `tenant_id`, `order_id`, `user_id`, and `passport_id`, then returns full synthetic passport detail plus a suggested audit event.

Future Falcon UI placement:

- Order Detail.
- New Order intake.
- Assignment workspace.

Visibility must remain internal-only. Client-facing views must not show Firm Intelligence cards, passport details, evidence links, audit metadata, reviewer notes, or internal comp/fact recommendations.

## Recommended Next 5 Slices

1. Permission policy contract tests for Falcon request wrappers: thread role/access decisions through the local Falcon card, passport, and evidence-open boundaries without production auth.
2. Audit event envelope snapshot: create a stable synthetic UI/API fixture for the audit payloads produced by the end-to-end workflow.
3. Production gate review packet template: add a documentation template for approvals, test plans, retention decisions, and rollback plans before any real content pilot.
4. First Falcon UI slice spec: turn `docs/falcon-ui-integration-notes.md` into a scoped implementation checklist for an internal-only Order Detail card preview.
5. Schema changelog template: add a documentation pattern for deliberate v2 schema proposals and fixture snapshot review.

## Current Known Risks

- Current matching is deterministic synthetic scoring, not production relevance logic.
- No production tenant isolation, auth, or permission enforcement exists.
- Permission policy is a local scaffold only and is not production auth.
- Suggested audit events are not persisted.
- Evidence links are placeholders and do not open source documents.
- Data passport fixtures cover only selected synthetic records.
- UI schemas are stable enough for prototype work but may need versioning as frontend requirements mature.
- Schema versions are registered, but only the card and passport drawer currently have committed UI snapshots.
- The repository contains no approved ingestion or extraction pipeline; adding one prematurely would violate the current safety boundary.
- Real content work remains blocked until the production readiness gate passes; metadata-only scans are the only allowed real-data activity.
- CI validates synthetic workflows only and cannot prove production readiness.
