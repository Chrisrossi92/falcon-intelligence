"""Metadata-only assignment profile export."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4

from falcon_intel.discovery import AssignmentCandidate, discover_assignments
from falcon_intel.search import ManifestSearchResult, search_manifest


DEFAULT_PROFILE_DIR = Path("data") / "profiles"
REPORT_EXTENSIONS = {".doc", ".docx"}
EXCEL_EXTENSIONS = {".xls", ".xlsx", ".xlsm"}
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".bmp", ".gif", ".heic", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class AssignmentProfile:
    """Bridge object from discovered folder metadata to future verified intelligence."""

    assignment_folder: str
    heuristic_label: str
    completeness_score: int
    counts_by_document_type: dict[str, int]
    file_groups: dict[str, list[dict[str, Any]]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_assignment_profile(
    manifest: dict[str, Any],
    assignment_folder: str,
) -> AssignmentProfile:
    """Build one metadata-only assignment profile from a manifest."""

    candidate = _find_candidate(manifest, assignment_folder)
    records = [
        result
        for result in search_manifest(manifest)
        if _record_assignment_folder(result.relative_path) == assignment_folder
    ]
    if not records:
        raise ValueError(f"Assignment folder not found: {assignment_folder}")

    file_groups = {
        "report_candidates": [],
        "excel_workbook_candidates": [],
        "photo_media_candidates": [],
        "pdf_source_document_candidates": [],
        "other_files": [],
    }
    for record in sorted(records, key=lambda item: item.relative_path.lower()):
        file_groups[_group_for(record)].append(_safe_file_record(record))

    return AssignmentProfile(
        assignment_folder=assignment_folder,
        heuristic_label=_heuristic_label(candidate),
        completeness_score=candidate.estimated_completeness_score,
        counts_by_document_type={
            "total_files": candidate.total_file_count,
            "documents": candidate.document_count,
            "pdf": candidate.pdf_count,
            "word": candidate.word_count,
            "excel": candidate.excel_count,
            "photos": candidate.photo_count,
            "map_images": candidate.map_image_count,
        },
        file_groups=file_groups,
    )


def save_assignment_profile(
    profile: AssignmentProfile,
    *,
    output_dir: str | Path = DEFAULT_PROFILE_DIR,
    file_name: str | None = None,
) -> Path:
    """Save an assignment profile under ignored local profile storage."""

    profile_dir = Path(output_dir)
    _require_profile_dir(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)

    output_name = file_name or f"profile-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}.json"
    if Path(output_name).name != output_name or not output_name.endswith(".json"):
        raise ValueError("Profile file name must be a local .json file name.")

    output_path = profile_dir / output_name
    output_path.write_text(json.dumps(profile.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def _find_candidate(manifest: dict[str, Any], assignment_folder: str) -> AssignmentCandidate:
    for candidate in discover_assignments(manifest):
        if candidate.assignment_folder == assignment_folder:
            return candidate
    raise ValueError(f"Assignment folder not found: {assignment_folder}")


def _record_assignment_folder(relative_path: str) -> str:
    path = PurePosixPath(relative_path)
    if len(path.parts) <= 1:
        return "."
    if _is_support_folder(path.parts[-2]) and len(path.parts) >= 3:
        return str(PurePosixPath(*path.parts[:-2]))
    return str(PurePosixPath(*path.parts[:-1]))


def _is_support_folder(folder_name: str) -> bool:
    return folder_name.lower() in {
        "aerials",
        "images",
        "maps",
        "photos",
        "plats",
        "support",
        "workbooks",
        "worksheets",
    }


def _safe_file_record(record: ManifestSearchResult) -> dict[str, Any]:
    return {
        "file_name": record.file_name,
        "file_extension": record.file_extension,
        "relative_path": record.relative_path,
        "file_size": record.file_size,
        "modified_timestamp": record.modified_timestamp,
        "supported_for_future_indexing": record.supported_for_future_indexing,
    }


def _group_for(record: ManifestSearchResult) -> str:
    if record.file_extension in REPORT_EXTENSIONS:
        return "report_candidates"
    if record.file_extension in EXCEL_EXTENSIONS:
        return "excel_workbook_candidates"
    if record.file_extension in IMAGE_EXTENSIONS:
        return "photo_media_candidates"
    if record.file_extension in PDF_EXTENSIONS:
        return "pdf_source_document_candidates"
    return "other_files"


def _heuristic_label(candidate: AssignmentCandidate) -> str:
    if candidate.heuristic.startswith("PDF + DOCX + Photos"):
        return "high-confidence-assignment"
    if candidate.heuristic.startswith("PDF only"):
        return "archived-report"
    if candidate.heuristic.startswith("DOCX + XLSX"):
        return "work-in-progress"
    if candidate.heuristic.startswith("Images only"):
        return "media-folder"
    return "review-candidate"


def _require_profile_dir(output_dir: Path) -> None:
    parts = [part.lower() for part in output_dir.parts]
    if len(parts) < 2 or parts[-2:] != ["data", "profiles"]:
        raise ValueError("Assignment profiles may only be saved under data/profiles/.")
