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

Search by file name keyword:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli search --manifest "data\manifests\scan-example.json" --name "report"
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

Discover probable assignment folders:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli discover --manifest "data\manifests\scan-example.json"
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

Save the profile under ignored local storage:

```powershell
$env:PYTHONPATH='src'
python -m falcon_intel.cli profile --manifest "data\manifests\scan-example.json" --assignment-folder "assignments/100-main" --save
```

## Output

CLI output is JSON so it can be reviewed or consumed by a future local UI. Results include metadata only.

## Safety Boundary

- `scan` uses filesystem metadata only.
- `search` reads manifest JSON only.
- `summary` reads manifest JSON only.
- `discover` reads manifest JSON only.
- `profile` reads manifest JSON only.
- Source files are never copied or opened for content.
- Manifest files remain local ignored prototype artifacts.
