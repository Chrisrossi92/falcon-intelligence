# Metadata-Only Manifest Search

Falcon Intelligence can search local scan manifests without touching source files.

Manifest search reads previously saved JSON manifests under local prototype storage and filters the metadata records they contain. It does not open original report files, extract text, OCR documents, copy files, create embeddings, or ingest report contents.

## Supported Filters

Search can filter manifest records by:

- File name keyword.
- File extension.
- Relative path keyword.
- Supported future-indexing flag.
- Modified timestamp range.

All filters operate on metadata captured by the scanner and saved in the manifest.

## Safe Results

Search results include:

- Selected root label.
- Manifest scan timestamp.
- File name.
- File extension.
- Relative path.
- File size.
- Modified timestamp.
- Supported future-indexing flag.

Absolute root paths are returned only when the manifest explicitly contains `absolute_root_path`. Manifests omit that field by default.

## Summaries

Summary helpers can report:

- Total files.
- Top extensions.
- Supported future-indexing files.
- Likely report candidates.

Likely report candidates are estimated only from extension, file name, and relative path patterns. This is a routing hint, not content analysis.

## Limitations

Manifest search cannot answer questions about report body content, comparable details, market narrative, values, clients, conclusions, or appraisal methodology. Those require content ingestion, which remains deferred behind a separate approval gate.

See `docs/cli.md` for PowerShell examples that run metadata-only search from the command line.
