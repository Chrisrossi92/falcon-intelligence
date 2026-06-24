# Assignment Discovery

Falcon Intelligence can estimate probable appraisal assignment folders from scan manifest metadata.

Assignment Discovery operates entirely on metadata that has already been captured in a local scan manifest. It does not open source files, read report contents, extract text, OCR documents, copy files, create embeddings, or infer values from report bodies.

## Candidate Fields

Each assignment candidate includes:

- Assignment folder.
- Total file count.
- Document count.
- Photo count.
- PDF count.
- Word count.
- Excel count.
- Map/image count.
- Estimated completeness score.
- Confidence label.
- Matching heuristic.

The CLI exposes these fields as metadata-only JSON with stable heuristic labels:

- `high-confidence-assignment`
- `archived-report`
- `work-in-progress`
- `media-folder`

## Folder Grouping

Discovery groups files by relative path. Common support folders such as `photos`, `maps`, `images`, `workbooks`, and `support` are treated as part of their parent assignment folder.

## Heuristics

Current metadata-only heuristics:

- PDF + DOCX + Photos = High confidence assignment.
- PDF only = Archived report.
- DOCX + XLSX = Work in progress.
- Images only = Media folder.
- Mixed metadata = Review candidate.

The completeness score is a rough metadata signal based on the presence of PDFs, Word documents, Excel files, and images. It is not a quality score and does not evaluate report content.

## Limitations

Assignment Discovery can be wrong when folders are named inconsistently, reports are stored outside assignment folders, or file names are misleading. Users should treat candidates as review prompts, not authoritative assignment records.
