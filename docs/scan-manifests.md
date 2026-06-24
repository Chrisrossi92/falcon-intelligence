# Local Scan Manifests

Falcon Intelligence can save metadata-only scan results into a local JSON manifest for prototype review.

The manifest is a local prototype artifact. It must be saved under `data/manifests/`, which is ignored by git. Manifests are not source documents, extracted report text, OCR output, embeddings, or an ingestion index.

## Manifest Contents

Each manifest includes:

- Manifest version.
- Scan timestamp.
- Selected root label.
- File metadata records from the scanner.
- Counts by file extension.
- Supported future-indexing count.

The selected root label is a user-facing label, not the absolute folder path. Absolute root paths are excluded by default.

## Absolute Path Privacy

Absolute paths may reveal client names, folder structures, or local OneDrive details. For that reason:

- `absolute_root_path` is omitted by default.
- The caller must explicitly request absolute path inclusion.
- The caller must provide the selected root path when absolute path inclusion is enabled.
- File records still use relative paths from the selected root.

## Storage Rule

Manifests may only be saved under `data/manifests/`. This keeps local prototype artifacts out of version control and makes accidental commits less likely.

## Content Guardrail

Manifest creation uses scanner metadata only. It does not read file contents, extract text, copy files, OCR documents, summarize reports, create embeddings, or ingest report content.

Manifest files can be searched by metadata only. See `docs/manifest-search.md` for search filters and limitations.
