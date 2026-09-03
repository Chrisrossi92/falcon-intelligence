# Local Intake Review Workflow

Local Intake Review is a synthetic/local proof for moving assignment-document candidates through appraiser judgment into AIR V1 and a concise Assignment/Property Brief.

## Run the Synthetic Proof

Preview the complete versioned workspace projection:

```bash
PYTHONPATH=src python -m falcon_intel.cli local-intake-review
```

Write deterministic local exports to an explicit ignored directory:

```bash
PYTHONPATH=src python -m falcon_intel.cli local-intake-review --export-dir data/local-intake-review/synthetic-northstar
```

The command writes AIR JSON, Brief V1 JSON, and Markdown. It refuses tracked repository destinations. The React preview consumes the same backend-generated synthetic semantic result.

## Appraiser Loop

1. Review the assignment overview drawn from current AIR facts.
2. Use topic, state, needs-attention, unresolved-conflict, or missing-critical views.
3. Review each value together with source document, locator, extraction method, confidence, quality, and evidence identity.
4. Accept supported values.
5. Correct values with a reason; the original observation/evidence remains.
6. Reject unsupported values with a reason; no candidate is deleted.
7. Defer when review cannot be completed; defer is not verification.
8. Resolve a conflict by selecting one value and explicitly rejecting competitors, or leave it unresolved.
9. Add an appraiser-entered dot-notation fact with reason and actor provenance.
10. Rebuild AIR and review readiness blockers.
11. Generate and inspect Brief V1.
12. Export only to an explicit safe local directory.

## Local Storage Rules

- Keep source documents outside the repository.
- Keep runtime review outputs under ignored `data/`, `exports/`, `local-data/`, or `local_data/`, or outside the repository entirely.
- Do not commit AIR exports, brief exports, extracted text, OCR output, databases, embeddings, or source documents.
- Committed demonstrations use the code-only synthetic Northstar facts and the generated JSON snapshot under `tests/fixtures/synthetic_intake_review/`.
- Do not put absolute user-specific paths into fixtures, docs, or source.

No durable review database is required for this proof. The Python service deterministically rebuilds AIR from immutable candidates/evidence and append-only review inputs; the React proof uses the backend-generated versioned fixture and keeps any additional interaction state in memory.

## Professional Boundary

The workflow separates verified facts, corrected facts, appraiser-entered facts, unresolved observations, and explicit professional conclusions. Completeness and readiness are workflow signals only. The workflow stops before appraisal narrative, value, highest and best use, final comparable selection, adjustments, or capitalization-rate decisions.

## Later Work-Computer Pilot Plan

Do not execute this pilot until the branch is merged and the work-computer checkout is synchronized.

1. Deliberately select one real assignment and no broader folder scope.
2. Keep all assignment documents outside the repository.
3. Use an ignored local output directory for extraction, review state, AIR, and brief exports.
4. Record extraction accuracy, false positives, and missed fields without copying confidential text into Git.
5. Compare review time with the current manual intake process.
6. Ask whether Brief V1 materially helps the appraiser start the report.
7. Confirm `git status` contains no confidential documents, extracted text, AIR/brief exports, local paths, databases, or debug artifacts.
8. Stop before narrative or valuation automation.

The pilot should be abandoned immediately if the selected scope expands, outputs appear in tracked paths, source text enters logs, or the brief implies unsupported professional conclusions.
