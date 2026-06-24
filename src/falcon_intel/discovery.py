"""Metadata-only assignment discovery over scan manifests."""

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable

from falcon_intel.search import ManifestSearchResult, search_manifest


DOCUMENT_EXTENSIONS = {".doc", ".docx", ".pdf", ".txt"}
EXCEL_EXTENSIONS = {".xls", ".xlsx", ".xlsm"}
IMAGE_EXTENSIONS = {".bmp", ".gif", ".heic", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
MAP_IMAGE_KEYWORDS = {"aerial", "fema", "flood", "gis", "location", "map", "parcel", "plat", "site", "tax"}


@dataclass(frozen=True)
class AssignmentCandidate:
    """Probable assignment folder estimated from file metadata only."""

    assignment_folder: str
    total_file_count: int
    document_count: int
    photo_count: int
    pdf_count: int
    word_count: int
    excel_count: int
    map_image_count: int
    estimated_completeness_score: int
    confidence_label: str
    heuristic: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "assignment_folder": self.assignment_folder,
            "total_file_count": self.total_file_count,
            "document_count": self.document_count,
            "photo_count": self.photo_count,
            "pdf_count": self.pdf_count,
            "word_count": self.word_count,
            "excel_count": self.excel_count,
            "map_image_count": self.map_image_count,
            "estimated_completeness_score": self.estimated_completeness_score,
            "confidence_label": self.confidence_label,
            "heuristic": self.heuristic,
        }


def discover_assignments(manifest: dict[str, Any]) -> list[AssignmentCandidate]:
    """Discover probable assignment folders from one metadata manifest."""

    folders: dict[str, list[ManifestSearchResult]] = {}
    for result in search_manifest(manifest):
        folder = _assignment_folder_for(result.relative_path)
        folders.setdefault(folder, []).append(result)

    candidates = [_build_candidate(folder, records) for folder, records in folders.items()]
    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate.estimated_completeness_score,
            candidate.assignment_folder.lower(),
        ),
    )


def _assignment_folder_for(relative_path: str) -> str:
    path = PurePosixPath(relative_path)
    if len(path.parts) <= 1:
        return "."
    if _is_support_folder(path.parts[-2]):
        if len(path.parts) >= 3:
            return str(PurePosixPath(*path.parts[:-2]))
    return str(PurePosixPath(*path.parts[:-1]))


def _is_support_folder(folder_name: str) -> bool:
    normalized = folder_name.lower()
    return normalized in {
        "aerials",
        "images",
        "maps",
        "photos",
        "plats",
        "support",
        "workbooks",
        "worksheets",
    }


def _build_candidate(folder: str, records: Iterable[ManifestSearchResult]) -> AssignmentCandidate:
    record_list = list(records)
    pdf_count = sum(1 for record in record_list if record.file_extension == ".pdf")
    word_count = sum(1 for record in record_list if record.file_extension in {".doc", ".docx"})
    excel_count = sum(1 for record in record_list if record.file_extension in EXCEL_EXTENSIONS)
    image_count = sum(1 for record in record_list if record.file_extension in IMAGE_EXTENSIONS)
    map_image_count = sum(1 for record in record_list if _is_map_image(record))
    document_count = sum(1 for record in record_list if record.file_extension in DOCUMENT_EXTENSIONS)

    heuristic = _heuristic(pdf_count, word_count, excel_count, image_count)
    return AssignmentCandidate(
        assignment_folder=folder,
        total_file_count=len(record_list),
        document_count=document_count,
        photo_count=max(image_count - map_image_count, 0),
        pdf_count=pdf_count,
        word_count=word_count,
        excel_count=excel_count,
        map_image_count=map_image_count,
        estimated_completeness_score=_score(pdf_count, word_count, excel_count, image_count),
        confidence_label=_confidence_label(heuristic),
        heuristic=heuristic,
    )


def _is_map_image(record: ManifestSearchResult) -> bool:
    if record.file_extension not in IMAGE_EXTENSIONS:
        return False
    text = f"{record.relative_path} {record.file_name}".lower()
    return any(keyword in text for keyword in MAP_IMAGE_KEYWORDS)


def _heuristic(pdf_count: int, word_count: int, excel_count: int, image_count: int) -> str:
    if pdf_count > 0 and word_count > 0 and image_count > 0:
        return "PDF + DOCX + Photos = High confidence assignment"
    if pdf_count > 0 and word_count == 0 and excel_count == 0 and image_count == 0:
        return "PDF only = Archived report"
    if pdf_count == 0 and word_count > 0 and excel_count > 0:
        return "DOCX + XLSX = Work in progress"
    if pdf_count == 0 and word_count == 0 and excel_count == 0 and image_count > 0:
        return "Images only = Media folder"
    return "Mixed metadata = Review candidate"


def _score(pdf_count: int, word_count: int, excel_count: int, image_count: int) -> int:
    score = 0
    if pdf_count > 0:
        score += 30
    if word_count > 0:
        score += 25
    if excel_count > 0:
        score += 15
    if image_count > 0:
        score += 20
    if pdf_count > 0 and word_count > 0 and image_count > 0:
        score += 10
    return min(score, 100)


def _confidence_label(heuristic: str) -> str:
    if heuristic.startswith("PDF + DOCX + Photos"):
        return "high"
    if heuristic.startswith("PDF only") or heuristic.startswith("DOCX + XLSX"):
        return "medium"
    if heuristic.startswith("Images only"):
        return "low"
    return "review"
