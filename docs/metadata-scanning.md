# Metadata-Only Folder Scanning

Falcon Intelligence can now define the foundation for safe folder scanning without ingesting report contents.

The scanner requires an explicit user-selected root folder and returns filesystem metadata only. It does not read file contents, extract text, copy files, OCR documents, create embeddings, summarize reports, or write an index.

## Recorded Fields

For each regular file under the selected root, the scanner records:

- File name.
- File extension.
- Relative path from the selected root.
- File size.
- Modified timestamp.
- Whether the extension is supported for future indexing.

Supported future file types are marked as metadata-only candidates:

- `.pdf`
- `.docx`
- `.xlsx`
- `.xls`
- `.txt`

## Safety Boundary

The scanner:

- Requires an explicit root folder argument.
- Walks only below that selected root.
- Skips symlinks.
- Uses filesystem metadata only.
- Does not include extracted text in its output model.

The metadata flag `supported_for_future_indexing` does not mean the file has been ingested. It only means the extension may be eligible for future indexing after a separate approval gate.

Metadata scan results can be saved as local JSON manifests. See `docs/scan-manifests.md` for manifest privacy rules.

## Deferred Ingestion

Content ingestion remains deferred. Future phases must define approval controls, local storage policy, redaction rules, audit logging, and synthetic test coverage before any report text extraction is added.
