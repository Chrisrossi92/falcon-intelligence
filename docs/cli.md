# Local Metadata CLI

Falcon Intelligence includes a local command-line interface for metadata-only prototype workflows.

The CLI can scan a user-selected folder into an ignored manifest, search a manifest by metadata, and summarize a manifest. It does not read source file contents, extract text, copy files, OCR documents, create embeddings, summarize reports, or ingest report content.

## Commands

Run the CLI through Python during local development:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli scan --root "C:\Path\To\SelectedFolder" --label "Friendly Name"
```

The `scan` command requires an explicit `--root`, saves under `data/manifests/`, and omits absolute paths by default.

To explicitly include the selected root path in the manifest:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli scan --root "C:\Path\To\SelectedFolder" --label "Friendly Name" --include-absolute-paths
```

Use that option carefully because absolute paths may reveal local folder names or client context.

List saved manifests:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli manifests
```

Search by file name keyword:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli search --manifest "data\manifests\scan-example.json" --name "report"
```

Search the latest saved manifest:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli search --latest --name "report"
```

Search by extension, relative path keyword, and supported future-indexing flag:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli search --manifest "data\manifests\scan-example.json" --extension ".pdf" --path "reports" --supported-only
```

Summarize a manifest:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli summary --manifest "data\manifests\scan-example.json"
```

Summarize the latest saved manifest:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli summary --latest
```

Discover probable assignment folders:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli discover --manifest "data\manifests\scan-example.json"
```

Discover assignments in the latest saved manifest:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli discover --latest
```

Filter discovery results by completeness score, heuristic label, and limit:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli discover --manifest "data\manifests\scan-example.json" --min-confidence 70 --label high-confidence-assignment --limit 10
```

Build a metadata-only assignment profile:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli profile --manifest "data\manifests\scan-example.json" --assignment-folder "assignments/100-main"
```

Build a profile from the latest saved manifest:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli profile --latest --assignment-folder "assignments/100-main"
```

Save the profile under ignored local storage:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli profile --manifest "data\manifests\scan-example.json" --assignment-folder "assignments/100-main" --save
```

Preview a synthetic "Firm Intelligence Found" card for a fake Falcon order:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli intelligence-card --address "1000 Example Industrial Way" --city "Sampleton" --state "ST" --property-type "industrial" --building-size-sf 50000 --client "Synthetic Lender A"
```

The `intelligence-card` command always uses the committed synthetic verified intelligence fixture by default. It returns the UI-facing card schema: headline, order summary, match group summaries, top match cards, confidence/provenance summary, warnings, and recommended actions.

Preview the synthetic Subject Profile and Report Field Registry workflow:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli subject-profile
```

Simulate appraiser review actions in the preview:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli subject-profile --approve assignment.property_rights --lock transaction.purchase_price
```

Preview the synthetic Property Library and Controlled Comp Vault workspace:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli property-library
```

Filter the Property Library preview:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli property-library --property-type Commercial --county "Montgomery County" --comp-role sale_comparable
```

Preview the synthetic Evidence Correction and Audit Trail workflow:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli correction-audit
```

## Output

CLI output is JSON so it can be reviewed or consumed by a future local UI. Results include metadata only.

## Safety Boundary

- `scan` uses filesystem metadata only.
- `manifests` reads local manifest JSON only.
- `search` reads manifest JSON only.
- `summary` reads manifest JSON only.
- `discover` reads manifest JSON only.
- `profile` reads manifest JSON only.
- `intelligence-card` reads the committed synthetic verified intelligence fixture only.
- `subject-profile` uses synthetic demo registry data only.
- `property-library` uses synthetic demo property, evidence, report usage, and candidate match data only.
- `correction-audit` uses synthetic correction, evidence reference, confidence impact, and audit history data only.
- Source files are never copied or opened for content.
- Manifest files remain local ignored prototype artifacts.
- The synthetic intelligence card preview does not use OneDrive data, report parsing, OCR, embeddings, or source-document content.

## Historical Intake Inventory

Run the local-only historical report intake inventory with a machine-specific config:

```bash
PYTHONPATH=src python scripts/historical-intake/run_historical_intake.py --config scripts/historical-intake/historical-intake.config.json
```

Start from the safe example config:

```text
scripts/historical-intake/historical-intake.config.example.json
```

For real sample calibration, copy the example to `scripts/historical-intake/historical-intake.config.local.json`, point `source_directories` at one approved small sample folder only, and run the same command with that local config. Keep the local config out of commits.

Generated outputs should be written under ignored local paths such as `data/historical-intake/`:

```text
historical-intake-report.json
historical-intake-report.csv
historical-intake-summary.md
```

The inventory is read-only. It records metadata, paths, filenames, folder names, timestamps, sizes, and hashes only. It does not parse report bodies, OCR files, call AI models, upload files, create production records, or modify source files.

When a real sample exposes new filename or folder patterns, convert those observations into anonymized synthetic tests. Do not commit real client names, addresses, order numbers, source paths, or generated inventory files.

## Historical Knowledge Extraction

Run local-only deterministic metadata extraction from the ignored historical intake JSON:

```bash
PYTHONPATH=src python scripts/historical-knowledge/run_historical_knowledge.py --intake data/historical-intake/historical-intake-report.json
```

Generated outputs are ignored under `data/historical-knowledge/`:

```text
historical-knowledge-report.json
historical-knowledge-summary.md
```

This phase considers likely final report PDFs, likely final report DOCX files, and same-order DOCX companion files from the intake output. It attempts embedded/searchable PDF text extraction when a local PDF text library is available and embedded DOCX text extraction when a local DOCX text library is available. It does not OCR scanned PDFs, parse spreadsheets/images, call AI models, create embeddings, upload files, write production records, or store full report text.

If the run reports that `pypdf` is not installed, enable optional local searchable-PDF support:

```bash
python -m pip install -e ".[pdf]"
```

This only enables embedded text extraction for searchable PDFs. Scanned PDFs still produce a no-searchable-text warning, and OCR remains out of scope.

If the run reports that `python-docx` is not installed, enable optional local DOCX support:

```bash
python -m pip install -e ".[docx]"
```

This only enables embedded text extraction for DOCX files already grouped by the intake inventory. DOCX-derived candidates carry `docx final report` or `docx companion source` provenance, and generated summaries do not include raw extracted document text.

## OCR/Layout Pilot

Run the privacy-safe OCR/layout pilot in availability-only mode:

```powershell
.\.venv\Scripts\python.exe scripts\run_ocr_layout_pilot.py --intake data\historical-intake\historical-intake-report.json --output-directory data\ocr-layout-pilot
```

Availability-only mode does not perform OCR. It records only whether the pilot would process the approved page buckets for `inspection_date` and `reviewer_name`.

To opt in to local OCR, install the optional Python wrappers and install the Tesseract executable separately on the Windows machine:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[ocr]"
```

Then run:

```powershell
.\.venv\Scripts\python.exe scripts\run_ocr_layout_pilot.py --intake data\historical-intake\historical-intake-report.json --output-directory data\ocr-layout-pilot --enable-ocr
```

The pilot does not save page images, screenshots, OCR text, snippets, raw extracted values, or source paths. Generated diagnostics stay under ignored `data/ocr-layout-pilot/` and include only anonymous report indexes, page buckets, target fields, anchor-family detection, candidate shapes, length buckets, fingerprints, and OCR availability or warning statuses. OCR-derived diagnostics are not wired into verification, promotion, Knowledge Objects, or the Memory Graph.

## Verification Engine

Run local deterministic verification from the ignored historical knowledge JSON:

```bash
PYTHONPATH=src python scripts/verification/run_verification.py --knowledge data/historical-knowledge/historical-knowledge-report.json
```

Generated outputs are ignored under `data/verification/`:

```text
verification-report.json
verification-summary.md
```

This phase promotes candidate metadata into local Verified Fact ledgers only when deterministic rules support the value. It records supporting evidence, conflicts, missing values, confidence, method, timestamp, and source references. It does not extract new report content, OCR, call AI, create embeddings, upload files, write production records, or create Knowledge Graph / Memory Graph records.

## Knowledge Object Builder

Run local deterministic Knowledge Object candidate building from the ignored verification JSON:

```bash
PYTHONPATH=src python scripts/knowledge/run_knowledge_objects.py --verification data/verification/verification-report.json
```

Generated outputs are ignored under `data/knowledge/`:

```text
knowledge-objects-report.json
knowledge-objects-summary.md
```

This phase groups Verified Facts into local Property, Report, Client/User, Personnel, and Open Issues candidates with readiness states. It does not create production schemas, upload data, parse source documents, call AI, or create Memory Graph records.

## Memory Graph Prototype

Run local deterministic Memory Graph building from the ignored Knowledge Object JSON:

```bash
PYTHONPATH=src python scripts/memory/run_memory_graph.py --knowledge-objects data/knowledge/knowledge-objects-report.json
```

Generated outputs are ignored under `data/memory/`:

```text
memory-graph-report.json
memory-graph-summary.md
```

This phase turns local Knowledge Object candidates into graph nodes and deterministic relationships. It does not create a production graph database, Supabase schema, backend API, embeddings, vector search, AI output, uploads, or real report ingestion.
