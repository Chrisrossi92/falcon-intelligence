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
- Source files are never copied or opened for content.
- Manifest files remain local ignored prototype artifacts.
- The synthetic intelligence card preview does not use OneDrive data, report parsing, OCR, embeddings, or source-document content.
