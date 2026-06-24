"""Synthetic/local evidence link model for future source navigation."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class EvidenceAccessLevel(StrEnum):
    """Stable access-level identifiers for evidence link visibility."""

    INTERNAL_ONLY = "internal_only"
    APPRAISER_REVIEWER_ONLY = "appraiser_reviewer_only"
    OWNER_ADMIN_ONLY = "owner_admin_only"
    DISABLED = "disabled"


EVIDENCE_ACCESS_LEVEL_CODES = tuple(level.value for level in EvidenceAccessLevel)


class EvidenceLinkStatus(StrEnum):
    """Local evidence-link lifecycle states."""

    AVAILABLE = "available"
    PLACEHOLDER = "placeholder"
    DISABLED = "disabled"


class EvidenceSourceDocumentType(StrEnum):
    """Synthetic source-document type identifiers."""

    SOURCE_REPORT = "source_report"
    SOURCE_DOCUMENT = "source_document"
    COMPARABLE_SUPPORT = "comparable_support"
    MARKET_SUPPORT = "market_support"


@dataclass(frozen=True)
class EvidenceLink:
    """Metadata-only pointer for future evidence opening behavior."""

    evidence_id: str
    tenant_id: str
    assignment_id: str
    source_document_id: str
    source_document_type: str
    display_label: str
    access_level: str
    future_page_number: int | None
    future_section_anchor: str | None
    future_highlight_text: str | None
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_source_report_evidence_link(
    *,
    evidence_id: str,
    tenant_id: str,
    assignment_id: str,
    source_document_id: str,
    display_label: str,
    access_level: EvidenceAccessLevel | str = EvidenceAccessLevel.INTERNAL_ONLY,
    future_page_number: int | None = None,
    future_section_anchor: str | None = None,
    future_highlight_text: str | None = None,
    status: EvidenceLinkStatus | str = EvidenceLinkStatus.PLACEHOLDER,
) -> EvidenceLink:
    """Create a metadata-only link to a synthetic source report record."""

    return build_evidence_link(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        source_document_id=source_document_id,
        source_document_type=EvidenceSourceDocumentType.SOURCE_REPORT,
        display_label=display_label,
        access_level=access_level,
        future_page_number=future_page_number,
        future_section_anchor=future_section_anchor,
        future_highlight_text=future_highlight_text,
        status=status,
    )


def build_source_document_evidence_link(
    *,
    evidence_id: str,
    tenant_id: str,
    assignment_id: str,
    source_document_id: str,
    display_label: str,
    access_level: EvidenceAccessLevel | str = EvidenceAccessLevel.INTERNAL_ONLY,
    future_page_number: int | None = None,
    future_section_anchor: str | None = None,
    future_highlight_text: str | None = None,
    status: EvidenceLinkStatus | str = EvidenceLinkStatus.PLACEHOLDER,
) -> EvidenceLink:
    """Create a metadata-only link to a synthetic source document record."""

    return build_evidence_link(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        source_document_id=source_document_id,
        source_document_type=EvidenceSourceDocumentType.SOURCE_DOCUMENT,
        display_label=display_label,
        access_level=access_level,
        future_page_number=future_page_number,
        future_section_anchor=future_section_anchor,
        future_highlight_text=future_highlight_text,
        status=status,
    )


def build_comparable_support_evidence_link(
    *,
    evidence_id: str,
    tenant_id: str,
    assignment_id: str,
    source_document_id: str,
    display_label: str,
    access_level: EvidenceAccessLevel | str = EvidenceAccessLevel.APPRAISER_REVIEWER_ONLY,
    future_page_number: int | None = None,
    future_section_anchor: str | None = None,
    future_highlight_text: str | None = None,
    status: EvidenceLinkStatus | str = EvidenceLinkStatus.PLACEHOLDER,
) -> EvidenceLink:
    """Create a metadata-only link to synthetic comparable support."""

    return build_evidence_link(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        source_document_id=source_document_id,
        source_document_type=EvidenceSourceDocumentType.COMPARABLE_SUPPORT,
        display_label=display_label,
        access_level=access_level,
        future_page_number=future_page_number,
        future_section_anchor=future_section_anchor,
        future_highlight_text=future_highlight_text,
        status=status,
    )


def build_market_support_evidence_link(
    *,
    evidence_id: str,
    tenant_id: str,
    assignment_id: str,
    source_document_id: str,
    display_label: str,
    access_level: EvidenceAccessLevel | str = EvidenceAccessLevel.INTERNAL_ONLY,
    future_page_number: int | None = None,
    future_section_anchor: str | None = None,
    future_highlight_text: str | None = None,
    status: EvidenceLinkStatus | str = EvidenceLinkStatus.PLACEHOLDER,
) -> EvidenceLink:
    """Create a metadata-only link to synthetic market support."""

    return build_evidence_link(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        source_document_id=source_document_id,
        source_document_type=EvidenceSourceDocumentType.MARKET_SUPPORT,
        display_label=display_label,
        access_level=access_level,
        future_page_number=future_page_number,
        future_section_anchor=future_section_anchor,
        future_highlight_text=future_highlight_text,
        status=status,
    )


def build_evidence_link(
    *,
    evidence_id: str,
    tenant_id: str,
    assignment_id: str,
    source_document_id: str,
    source_document_type: EvidenceSourceDocumentType | str,
    display_label: str,
    access_level: EvidenceAccessLevel | str,
    future_page_number: int | None = None,
    future_section_anchor: str | None = None,
    future_highlight_text: str | None = None,
    status: EvidenceLinkStatus | str = EvidenceLinkStatus.PLACEHOLDER,
) -> EvidenceLink:
    """Build one validated metadata-only evidence link."""

    _require_non_empty("evidence_id", evidence_id)
    _require_non_empty("tenant_id", tenant_id)
    _require_non_empty("assignment_id", assignment_id)
    _require_non_empty("source_document_id", source_document_id)
    _require_non_empty("display_label", display_label)

    active_source_type = EvidenceSourceDocumentType(source_document_type)
    active_access_level = EvidenceAccessLevel(access_level)
    active_status = EvidenceLinkStatus(status)
    if active_access_level == EvidenceAccessLevel.DISABLED and active_status != EvidenceLinkStatus.DISABLED:
        active_status = EvidenceLinkStatus.DISABLED
    if future_page_number is not None and future_page_number < 1:
        raise ValueError("future_page_number must be greater than zero when provided.")

    return EvidenceLink(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        source_document_id=source_document_id,
        source_document_type=active_source_type.value,
        display_label=display_label,
        access_level=active_access_level.value,
        future_page_number=future_page_number,
        future_section_anchor=_clean_optional(future_section_anchor),
        future_highlight_text=_clean_optional(future_highlight_text),
        status=active_status.value,
    )


def _require_non_empty(field_name: str, value: str | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
