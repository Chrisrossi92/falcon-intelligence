# Falcon Historical Intake Pipeline

This document defines the local-only Historical Report Intake Inventory approach for Falcon Intelligence. It is documentation-only for product architecture and is supported by a local staging tool. It does not authorize OCR, AI extraction, embeddings, vector databases, OneDrive integration, Supabase schemas, production APIs, real uploads, source-file modification, or report text extraction.

## Purpose

Falcon Intelligence will eventually learn from two sources:

- Historical orders and reports that already exist in firm-controlled folders, exports, PDFs, spreadsheets, photos, maps, and supporting documents.
- Future orders and reports uploaded through a controlled Falcon workflow.

This pipeline covers only the historical side. Its purpose is to answer:

```text
What historical files exist, where are they, what do they appear to represent,
and how ready are they for future ingestion?
```

It is an inventory and staging layer, not an ingestion layer.

## Staging-First Approach

Historical intake should happen in stages:

```text
Local folders
-> Metadata inventory
-> Duplicate review
-> Candidate order grouping
-> Readiness classification
-> Future approved ingestion planning
```

The current local tool stops at readiness classification. It writes local reports only and does not alter source files.

## Local Inventory Behavior

The local inventory tool:

- Scans configured source directories.
- Includes configured file extensions.
- Excludes configured folders.
- Records file path, filename, extension, size, timestamps, parent folder, and SHA-256 hash.
- Infers likely order identifier, property address, client, report type, report date, and candidate file role from filename and folder heuristics only.
- Detects conservative duplicate groups.
- Groups files into candidate historical order packages.
- Classifies readiness with explainable rules.
- Writes JSON, CSV, and Markdown summary outputs under a local output directory.

Candidate roles are:

- Final report.
- Draft report.
- Engagement letter.
- Source document.
- Photo.
- Map.
- Rent roll.
- Unknown.

## Duplicate Detection

Duplicate detection is conservative and non-destructive.

Duplicate group types:

| Type | Meaning |
| --- | --- |
| Exact hash | Files have the same SHA-256 hash. |
| Likely name and size | Files have the same normalized filename and file size. |
| Possible order / property / date | Files share at least two of order identifier, property address, and report date. |

The tool never deletes, moves, renames, suppresses, or merges duplicates. It reports candidate groups for human cleanup planning.

## Candidate Order Grouping

Files are grouped into preliminary historical order packages using:

- Shared likely order identifier.
- Shared likely property address.
- Shared parent folder.
- Single-file fallback when no stronger signal exists.

Each group records:

- Candidate group ID.
- Included file IDs.
- Confidence level.
- Grouping key and reason.
- Likely order identifier.
- Likely property address.
- Likely client.
- Likely report date.
- Likely primary report.
- Missing or unknown fields.
- Readiness classification and reason.

## Readiness Classification

Readiness classifications are rule-based:

| Classification | Meaning |
| --- | --- |
| Ready for future extraction | Likely final report and supporting materials are present. |
| Needs review | Likely final report exists, but package context is limited. |
| Missing final report | No likely final report is present, or only a draft report was identified. |
| Duplicate-heavy | Multiple files in the package appear in exact or likely duplicate groups. |
| Unknown / insufficient metadata | Most files cannot be classified from metadata heuristics. |

These classifications are planning signals only. They do not authorize extraction or ingestion.

## Historical Intake vs Future Direct Uploads

Historical intake is retrospective. It inventories uncontrolled legacy folders and prepares cleanup decisions.

Future direct uploads are prospective. They should happen through a controlled Falcon workflow with explicit permissions, assignment context, uploader identity, audit events, file policy, retention policy, and production gates.

Historical intake should not become a hidden upload pathway. It should prepare safe migration and ingestion decisions after approval.

Future clean uploads should also preserve a preferred appraisal workfile structure:

- Final report.
- Engagement letter.
- Source documents.
- Rent roll and financials.
- Maps.
- Photos.
- Comparable data.
- Reviewer notes.
- Revision history.

This future-facing discipline keeps Falcon from relying on ad hoc folders indefinitely and makes future extraction, audit, and institutional memory easier to verify.

## Privacy and Safety Rules

The historical intake tool must:

- Remain read-only against source folders.
- Never move, rename, delete, or modify source files.
- Never upload files.
- Never parse full PDF, DOCX, spreadsheet, text, XML, or image contents.
- Never OCR.
- Never call AI models.
- Never create embeddings or vector stores.
- Never write Supabase schemas or production records.
- Never include sensitive document body text in outputs.
- Use metadata, paths, filenames, folder names, timestamps, sizes, and hashes only.

Hashing reads file bytes to compute duplicate fingerprints. It is not content parsing and must not produce excerpts, summaries, or extracted fields.

## Relationship to the Intelligence Engine

Historical intake is a pre-engine staging layer. It prepares the future source inventory that may eventually feed the canonical Intelligence Engine:

```text
Documents
-> Facts
-> Knowledge
-> Insights
-> Recommendations
-> Actions
```

Current historical intake operates before `Documents` are approved as source evidence. It does not create facts, knowledge objects, insights, recommendations, or actions.

Phase 1 Historical Knowledge Extraction is the next local-only step after intake. It can produce deterministic metadata candidates from likely final reports, but those candidates are not verified facts or Knowledge Model objects until a future verification layer promotes them.

## Alternate Text Extraction and OCR Planning

After metadata-only intake, local historical knowledge extraction may use embedded text from approved local files without changing the source folders. The first alternate source is DOCX because embedded Word text is simpler and less risky than OCR. DOCX extraction is optional, local-only, and limited to likely final DOCX files or DOCX companions in the same candidate order group as a likely final report. DOCX-derived candidates must carry explicit provenance such as `docx final report` or `docx companion source`.

OCR is only needed when an approved likely final report or same-order evidence file has no searchable PDF text and no usable embedded DOCX companion. OCR outputs should live only under ignored local paths, such as a future `data/ocr-cache/` or run-specific extraction cache, and should be treated as sensitive derived document text. OCR output must not be committed, printed in terminal summaries, copied into docs, uploaded, embedded, or used to create production records without a separate approval gate.

OCR is not enabled by default because it is heavier, slower, error-prone, and more likely to expose private report body text. It also introduces operational dependencies, image preprocessing choices, retention questions, and review obligations that are outside the current deterministic metadata slice.

Future approved ingestion may use the inventory to decide:

- Which folders are ready for controlled ingestion.
- Which duplicate groups require cleanup.
- Which packages need human review before extraction.
- Which source files may become evidence candidates.
- Which historical orders can eventually seed the firm's Memory Graph and Knowledge Model.

## Memory Graph Boundary

The Memory Graph is a future concept for connected firm knowledge. Historical intake may eventually feed it by identifying source packages and provenance candidates. The current tool does not create graph nodes, relationships, embeddings, or searchable knowledge.

## Local Tooling

The local implementation lives in:

- `src/falcon_intel/historical_intake.py`
- `scripts/historical-intake/run_historical_intake.py`
- `scripts/historical-intake/historical-intake.config.example.json`

Generated outputs should be written under ignored local paths such as:

```text
data/historical-intake/
```

Expected output files:

```text
historical-intake-report.json
historical-intake-report.csv
historical-intake-summary.md
```

Real machine-specific config should use:

```text
scripts/historical-intake/historical-intake.config.json
scripts/historical-intake/historical-intake.config.local.json
```

Those files are ignored by git.

## Sample Calibration Workflow

Before scanning a full historical archive, calibrate against one approved small sample folder. A good sample is either 20-50 files or one known appraisal/order folder with a manageable number of report and support documents.

1. Copy the example config:

```text
scripts/historical-intake/historical-intake.config.example.json
```

to an ignored local config:

```text
scripts/historical-intake/historical-intake.config.local.json
```

2. Set `source_directories` to the approved sample folder only. Do not point calibration at the full archive.

3. Run the intake locally:

```bash
PYTHONPATH=src python scripts/historical-intake/run_historical_intake.py --config scripts/historical-intake/historical-intake.config.local.json
```

4. Review only the generated local summary and inventory metrics:

```text
data/historical-intake/historical-intake-summary.md
data/historical-intake/historical-intake-report.json
data/historical-intake/historical-intake-report.csv
```

5. Improve heuristics by translating observed real-world patterns into anonymized synthetic tests. Do not commit real paths, client names, property addresses, order numbers, filenames, or generated outputs.

6. Re-run the synthetic tests and smoke checks before scanning another sample.

It is safe to scale from a sample to a larger archive only after the sample produces reasonable candidate groups, low unexplained unknown counts, no unexpected source-folder access, and no sensitive generated output has been staged for commit.

## Current Guardrail

This pipeline is a safe inventory scaffold only. It helps the firm understand historical material before any future ingestion decision. It must not be treated as extraction, import, document viewing, AI analysis, production indexing, or Memory Graph creation.
