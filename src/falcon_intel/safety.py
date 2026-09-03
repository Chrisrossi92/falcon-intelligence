"""Safety helpers for local file handling."""

from pathlib import Path


BLOCKED_SUFFIXES = {
    ".7z",
    ".bmp",
    ".csv",
    ".db",
    ".doc",
    ".docx",
    ".faiss",
    ".gif",
    ".gz",
    ".heic",
    ".index",
    ".jpeg",
    ".jpg",
    ".jsonl",
    ".ndjson",
    ".ocr",
    ".parquet",
    ".pdf",
    ".png",
    ".rar",
    ".rtf",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tif",
    ".tiff",
    ".tgz",
    ".tsv",
    ".txt",
    ".webp",
    ".xls",
    ".xlsb",
    ".xlsm",
    ".xlsx",
    ".zip",
}


def is_blocked_source_path(path: str | Path) -> bool:
    candidate = Path(path)
    parts = {part.lower() for part in candidate.parts}
    if parts.intersection(
        {
            "archives",
            "client-files",
            "client_files",
            "data",
            "databases",
            "documents",
            "embeddings",
            "extracted",
            "extracted-text",
            "extracted_text",
            "exports",
            "ingest",
            "incoming",
            "indexes",
            "layout-analysis",
            "layout_analysis",
            "local-data",
            "local_data",
            "onedrive",
            "ocr",
            "ocr-cache",
            "ocr-output",
            "ocr_cache",
            "ocr_output",
            "private",
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
