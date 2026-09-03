"""Fail when tracked files or ignore rules cross repository privacy boundaries."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DOCUMENT_ROOT = Path("tests/fixtures/synthetic_sample_data")
SYNTHETIC_PLACEHOLDER_HEADER = "SYNTHETIC PLACEHOLDER ONLY."
MAX_SYNTHETIC_PLACEHOLDER_BYTES = 4096
BLOCKED_TRACKED_SUFFIXES = {
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
IGNORED_PATH_SAMPLES = (
    "data/historical-knowledge/historical-knowledge-report.json",
    "data/ocr-layout-pilot/diagnostics.json",
    "data/embeddings/client-material.faiss",
    "local_data/falcon.sqlite",
    "source_documents/report.pdf",
    "client_files/workfile.xlsx",
    "exports/extracted-report.txt",
    "private/photos/inspection.jpg",
    "archives/assignment.zip",
    "embeddings/assignment-vectors.json",
    "ocr-output/page-artifact",
    "layout-analysis/page-layout.json",
    ".env.local",
)
ALLOWED_PATH_SAMPLES = (
    "tests/fixtures/synthetic_sample_data/example.pdf",
    "tests/fixtures/synthetic_sample_data/example.docx",
    "tests/fixtures/synthetic_sample_data/example.xlsx",
    "tests/fixtures/synthetic_sample_data/example.jpg",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _repository_paths() -> tuple[Path, ...]:
    result = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return tuple(Path(item) for item in result.stdout.split("\0") if item)


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def main() -> int:
    errors: list[str] = []
    for relative_path in _repository_paths():
        if relative_path.suffix.lower() not in BLOCKED_TRACKED_SUFFIXES:
            continue
        if not _is_under(relative_path, SYNTHETIC_DOCUMENT_ROOT):
            errors.append(f"prohibited tracked source/data file: {relative_path.as_posix()}")
            continue

        fixture_path = REPO_ROOT / relative_path
        payload = fixture_path.read_bytes()
        if len(payload) > MAX_SYNTHETIC_PLACEHOLDER_BYTES:
            errors.append(f"synthetic document fixture is too large: {relative_path.as_posix()}")
            continue
        try:
            fixture_text = payload.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"synthetic document fixture is not a text placeholder: {relative_path.as_posix()}")
            continue
        if not fixture_text.startswith(SYNTHETIC_PLACEHOLDER_HEADER):
            errors.append(f"synthetic document fixture lacks the required marker: {relative_path.as_posix()}")

    for sample in IGNORED_PATH_SAMPLES:
        result = _git("check-ignore", "--quiet", "--no-index", sample)
        if result.returncode != 0:
            errors.append(f"privacy-sensitive path is not ignored: {sample}")

    for sample in ALLOWED_PATH_SAMPLES:
        result = _git("check-ignore", "--quiet", "--no-index", sample)
        if result.returncode == 0:
            errors.append(f"synthetic fixture convention is accidentally ignored: {sample}")

    if errors:
        print("Repository safety/privacy check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Repository safety/privacy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
