"""UI-facing synthetic passport detail drawer schema."""

from dataclasses import asdict, dataclass
from typing import Any

from falcon_intel.match_policy import WarningCode
from falcon_intel.schema_registry import PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION


@dataclass(frozen=True)
class PassportDrawerIdentity:
    """Stable identity block for a passport detail drawer."""

    passport_id: str
    fact_id: str
    tenant_id: str
    assignment_id: str


@dataclass(frozen=True)
class PassportDrawerFactSummary:
    """Fact summary shown at the top of the drawer."""

    fact_type: str
    display_label: str
    display_value: str


@dataclass(frozen=True)
class PassportDrawerVerificationSummary:
    """Verification and review summary for trusted fact display."""

    verification_status: str
    verified_by: str
    verified_at: str
    reviewed_by: str | None
    reviewed_at: str | None


@dataclass(frozen=True)
class PassportDrawerEvidenceLinkSummary:
    """Compact evidence link summary for drawer rows."""

    evidence_id: str
    source_document_type: str
    display_label: str
    access_level: str
    status: str
    has_future_anchor: bool


@dataclass(frozen=True)
class PassportDrawerWarning:
    """UI warning shown in the passport detail drawer."""

    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class PassportDetailDrawer:
    """Stable UI-facing schema for the future Falcon passport detail drawer."""

    schema_version: str
    passport_identity: PassportDrawerIdentity
    fact_summary: PassportDrawerFactSummary
    verification_review_summary: PassportDrawerVerificationSummary
    confidence_dimensions: dict[str, str]
    evidence_links_summary: list[PassportDrawerEvidenceLinkSummary]
    audit_event_ids: list[str]
    searchable_status: str
    warnings: list[PassportDrawerWarning]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_passport_detail_drawer(passport_detail: dict[str, Any]) -> PassportDetailDrawer:
    """Serialize full synthetic passport detail into a stable drawer schema."""

    warnings = _warnings(passport_detail)
    return PassportDetailDrawer(
        schema_version=PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION,
        passport_identity=PassportDrawerIdentity(
            passport_id=str(passport_detail["passport_id"]),
            fact_id=str(passport_detail["fact_id"]),
            tenant_id=str(passport_detail["tenant_id"]),
            assignment_id=str(passport_detail["assignment_id"]),
        ),
        fact_summary=PassportDrawerFactSummary(
            fact_type=str(passport_detail["fact_type"]),
            display_label=str(passport_detail["display_label"]),
            display_value=str(passport_detail["display_value"]),
        ),
        verification_review_summary=PassportDrawerVerificationSummary(
            verification_status=str(passport_detail["verification_status"]),
            verified_by=str(passport_detail["verified_by"]),
            verified_at=str(passport_detail["verified_at"]),
            reviewed_by=passport_detail.get("reviewed_by"),
            reviewed_at=passport_detail.get("reviewed_at"),
        ),
        confidence_dimensions=dict(passport_detail["confidence_dimensions"]),
        evidence_links_summary=[
            _evidence_link_summary(link)
            for link in passport_detail.get("evidence_links", [])
        ],
        audit_event_ids=list(passport_detail.get("audit_event_ids", [])),
        searchable_status=str(passport_detail["searchable_status"]),
        warnings=warnings,
    )


def _evidence_link_summary(link: dict[str, Any]) -> PassportDrawerEvidenceLinkSummary:
    return PassportDrawerEvidenceLinkSummary(
        evidence_id=str(link["evidence_id"]),
        source_document_type=str(link["source_document_type"]),
        display_label=str(link["display_label"]),
        access_level=str(link["access_level"]),
        status=str(link["status"]),
        has_future_anchor=bool(
            link.get("future_page_number")
            or link.get("future_section_anchor")
            or link.get("future_highlight_text")
        ),
    )


def _warnings(passport_detail: dict[str, Any]) -> list[PassportDrawerWarning]:
    warnings = [
        PassportDrawerWarning(
            code=WarningCode.SYNTHETIC_PREVIEW_ONLY.value,
            severity="info",
            message="Synthetic passport detail only; do not use as production firm intelligence.",
        )
    ]
    if any(link.get("status") == "placeholder" for link in passport_detail.get("evidence_links", [])):
        warnings.append(
            PassportDrawerWarning(
                code="evidence_placeholder_only",
                severity="info",
                message="Evidence links are metadata placeholders and do not open source documents.",
            )
        )
    if passport_detail.get("verification_status") != "verified":
        warnings.append(
            PassportDrawerWarning(
                code=WarningCode.APPRAISER_REVIEW_REQUIRED.value,
                severity="warning",
                message="Passport detail is not verified and requires appraiser review.",
            )
        )
    return warnings
