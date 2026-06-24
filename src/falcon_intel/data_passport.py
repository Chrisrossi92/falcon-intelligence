"""Synthetic/local data passport model for verified fact provenance."""

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from falcon_intel.evidence_link import EvidenceLink


class VerificationStatus(StrEnum):
    """Stable verification status identifiers for local data passports."""

    VERIFIED = "verified"
    REVIEWED = "reviewed"
    SUGGESTED = "suggested"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class SearchableStatus(StrEnum):
    """Stable searchability identifiers for verified intelligence."""

    SEARCHABLE = "searchable"
    RESTRICTED = "restricted"
    NOT_SEARCHABLE = "not_searchable"


@dataclass(frozen=True)
class ConfidenceDimensions:
    """Multi-dimensional confidence display for one verified fact."""

    extraction_confidence: str
    source_quality: str
    source_agreement: str
    freshness: str
    reviewer_approval: str
    historical_consistency: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class DataPassport:
    """Synthetic/local trust card for one verified fact."""

    fact_id: str
    tenant_id: str
    assignment_id: str
    fact_type: str
    display_label: str
    display_value: str
    verification_status: str
    verified_by: str
    verified_at: str
    reviewed_by: str | None
    reviewed_at: str | None
    confidence_dimensions: ConfidenceDimensions
    evidence_links: list[dict[str, Any]]
    audit_event_ids: list[str]
    searchable_status: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["confidence_dimensions"] = self.confidence_dimensions.to_dict()
        payload["evidence_links"] = [dict(link) for link in self.evidence_links]
        payload["audit_event_ids"] = list(self.audit_event_ids)
        return payload


def build_confidence_dimensions(
    *,
    extraction_confidence: str,
    source_quality: str,
    source_agreement: str,
    freshness: str,
    reviewer_approval: str,
    historical_consistency: str,
) -> ConfidenceDimensions:
    """Build validated confidence dimensions for a synthetic data passport."""

    values = {
        "extraction_confidence": extraction_confidence,
        "source_quality": source_quality,
        "source_agreement": source_agreement,
        "freshness": freshness,
        "reviewer_approval": reviewer_approval,
        "historical_consistency": historical_consistency,
    }
    for field_name, value in values.items():
        _require_non_empty(field_name, value)
    return ConfidenceDimensions(**values)


def build_data_passport(
    *,
    fact_id: str,
    tenant_id: str,
    assignment_id: str,
    fact_type: str,
    display_label: str,
    display_value: str,
    verification_status: VerificationStatus | str,
    verified_by: str,
    verified_at: str,
    confidence_dimensions: ConfidenceDimensions | Mapping[str, str],
    evidence_links: Sequence[EvidenceLink | Mapping[str, Any]],
    searchable_status: SearchableStatus | str,
    reviewed_by: str | None = None,
    reviewed_at: str | None = None,
    audit_event_ids: Sequence[str] | None = None,
) -> DataPassport:
    """Build one validated synthetic/local data passport object."""

    _require_non_empty("fact_id", fact_id)
    _require_non_empty("tenant_id", tenant_id)
    _require_non_empty("assignment_id", assignment_id)
    _require_non_empty("fact_type", fact_type)
    _require_non_empty("display_label", display_label)
    _require_non_empty("display_value", display_value)
    _require_non_empty("verified_by", verified_by)
    _require_non_empty("verified_at", verified_at)
    active_verification_status = VerificationStatus(verification_status)
    active_searchable_status = SearchableStatus(searchable_status)
    active_confidence_dimensions = _coerce_confidence_dimensions(confidence_dimensions)
    active_evidence_links = _coerce_evidence_links(evidence_links)
    active_audit_event_ids = _coerce_audit_event_ids(audit_event_ids)

    return DataPassport(
        fact_id=fact_id,
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        fact_type=fact_type,
        display_label=display_label,
        display_value=display_value,
        verification_status=active_verification_status.value,
        verified_by=verified_by,
        verified_at=verified_at,
        reviewed_by=_clean_optional(reviewed_by),
        reviewed_at=_clean_optional(reviewed_at),
        confidence_dimensions=active_confidence_dimensions,
        evidence_links=active_evidence_links,
        audit_event_ids=active_audit_event_ids,
        searchable_status=active_searchable_status.value,
    )


def _coerce_confidence_dimensions(
    confidence_dimensions: ConfidenceDimensions | Mapping[str, str],
) -> ConfidenceDimensions:
    if isinstance(confidence_dimensions, ConfidenceDimensions):
        return confidence_dimensions
    required_fields = {
        "extraction_confidence",
        "source_quality",
        "source_agreement",
        "freshness",
        "reviewer_approval",
        "historical_consistency",
    }
    missing = sorted(required_fields - set(confidence_dimensions))
    if missing:
        raise ValueError(f"confidence_dimensions missing required fields: {', '.join(missing)}")
    return build_confidence_dimensions(
        extraction_confidence=confidence_dimensions["extraction_confidence"],
        source_quality=confidence_dimensions["source_quality"],
        source_agreement=confidence_dimensions["source_agreement"],
        freshness=confidence_dimensions["freshness"],
        reviewer_approval=confidence_dimensions["reviewer_approval"],
        historical_consistency=confidence_dimensions["historical_consistency"],
    )


def _coerce_evidence_links(
    evidence_links: Sequence[EvidenceLink | Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not evidence_links:
        raise ValueError("evidence_links is required.")

    payload: list[dict[str, Any]] = []
    for index, link in enumerate(evidence_links):
        link_payload = link.to_dict() if isinstance(link, EvidenceLink) else dict(link)
        for field_name in (
            "evidence_id",
            "tenant_id",
            "assignment_id",
            "source_document_id",
            "source_document_type",
            "display_label",
            "access_level",
            "status",
        ):
            _require_non_empty(f"evidence_links[{index}].{field_name}", link_payload.get(field_name))
        payload.append(link_payload)
    return payload


def _coerce_audit_event_ids(audit_event_ids: Sequence[str] | None) -> list[str]:
    if audit_event_ids is None:
        return []
    payload = list(audit_event_ids)
    for index, event_id in enumerate(payload):
        _require_non_empty(f"audit_event_ids[{index}]", event_id)
    return payload


def _require_non_empty(field_name: str, value: Any | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
