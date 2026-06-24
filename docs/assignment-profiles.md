# Assignment Profiles

Falcon Intelligence can build a metadata-only assignment profile for one discovered assignment folder.

An assignment profile is the bridge between folder discovery and future verified intelligence extraction. It organizes known metadata into reviewable groups without opening source files, reading report contents, extracting text, copying files, OCRing documents, creating embeddings, or ingesting report data.

## Profile Fields

Each profile includes:

- Assignment folder.
- Heuristic label.
- Completeness score.
- Counts by document type.
- Categorized file groups.

## File Groups

Profile file groups are based only on file name, extension, and relative path:

- `report_candidates`
- `excel_workbook_candidates`
- `photo_media_candidates`
- `pdf_source_document_candidates`
- `other_files`

The groups are routing hints for future review. They do not imply that a file has been read or verified.

## Local Storage

Profiles may be saved under `data/profiles/`, which is ignored by git. Saved profiles are local prototype artifacts and may contain file names and relative paths.

## Guardrail

Assignment profiles are not verified intelligence records. They are metadata-only summaries that can support a future appraiser-approved extraction workflow after a separate approval gate.

See `docs/verified-intelligence-workflow.md` for the future review workflow that would govern any extracted suggestions.
