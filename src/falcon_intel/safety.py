"""Safety helpers for future file handling."""

from pathlib import Path


BLOCKED_SUFFIXES = {
    ".csv",
    ".db",
    ".doc",
    ".docx",
    ".faiss",
    ".index",
    ".jsonl",
    ".ndjson",
    ".ocr",
    ".parquet",
    ".pdf",
    ".rtf",
    ".sqlite",
    ".sqlite3",
    ".tsv",
    ".txt",
    ".xls",
    ".xlsm",
    ".xlsx",
}


def is_blocked_source_path(path: str | Path) -> bool:
    candidate = Path(path)
    parts = {part.lower() for part in candidate.parts}
    if parts.intersection(
        {
            "data",
            "documents",
            "extracted",
            "extracted-text",
            "extracted_text",
            "ingest",
            "incoming",
            "local-data",
            "local_data",
            "onedrive",
            "reports",
            "source-docs",
            "source-documents",
            "source_documents",
            "source_docs",
            "uploads",
        }
    ):
        return True
    return candidate.suffix.lower() in BLOCKED_SUFFIXES
