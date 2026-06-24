"""Local in-memory contract boundary for future Falcon evidence-open events."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from falcon_intel.audit import build_evidence_opened_event
from falcon_intel.data_passport_lookup import (
    DEFAULT_DATA_PASSPORT_FIXTURE_PATH,
    lookup_data_passport_detail,
)
from falcon_intel.permission_policy import can_open_evidence_link
from falcon_intel.schema_registry import FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION


REQUIRED_EVIDENCE_OPEN_FIELDS = (
    "tenant_id",
    "order_id",
    "user_id",
    "passport_id",
    "evidence_id",
)


@dataclass(frozen=True)
class FalconEvidenceOpenBoundaryResponse:
    """In-memory stand-in for a future Falcon evidence-open API/RPC response."""

    status: str
    tenant_id: str | None
    order_id: str | None
    user_id: str | None
    passport_id: str | None
    evidence_id: str | None
    schema_version: str = FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION
    evidence_summary: dict[str, Any] | None = None
    suggested_audit_event: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    reason_code: str | None = None
    reason_label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "tenant_id": self.tenant_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "passport_id": self.passport_id,
            "evidence_id": self.evidence_id,
            "schema_version": self.schema_version,
        }
        if self.evidence_summary is not None:
            payload["evidence_summary"] = self.evidence_summary
        if self.suggested_audit_event is not None:
            payload["suggested_audit_event"] = self.suggested_audit_event
        if self.error is not None:
            payload["error"] = self.error
        if self.reason_code is not None:
            payload["reason_code"] = self.reason_code
        if self.reason_label is not None:
            payload["reason_label"] = self.reason_label
        return payload


def build_falcon_evidence_open_response(
    request_payload: dict[str, Any],
    *,
    synthetic_passport_path: str | Path = DEFAULT_DATA_PASSPORT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Return a safe synthetic evidence-open response for a passport evidence link."""

    missing_fields = [
        field
        for field in REQUIRED_EVIDENCE_OPEN_FIELDS
        if field not in request_payload or request_payload[field] in (None, "")
    ]
    tenant_id = _optional_str(request_payload.get("tenant_id"))
    order_id = _optional_str(request_payload.get("order_id"))
    user_id = _optional_str(request_payload.get("user_id"))
    passport_id = _optional_str(request_payload.get("passport_id"))
    evidence_id = _optional_str(request_payload.get("evidence_id"))
    if missing_fields:
        return FalconEvidenceOpenBoundaryResponse(
            status="missing_required_input",
            tenant_id=tenant_id,
            order_id=order_id,
            user_id=user_id,
            passport_id=passport_id,
            evidence_id=evidence_id,
            error={
                "code": "missing_required_input",
                "message": "Falcon evidence-open payload is missing required fields.",
                "missing_fields": missing_fields,
            },
        ).to_dict()

    lookup_response = lookup_data_passport_detail(
        tenant_id=str(tenant_id),
        passport_id=str(passport_id),
        fixture_path=synthetic_passport_path,
    ).to_dict()
    if lookup_response["status"] != "found":
        return FalconEvidenceOpenBoundaryResponse(
            status="not_found",
            tenant_id=tenant_id,
            order_id=order_id,
            user_id=user_id,
            passport_id=passport_id,
            evidence_id=evidence_id,
            error={
                "code": "passport_not_found",
                "message": "No synthetic data passport found for tenant and passport_id.",
            },
        ).to_dict()

    passport = lookup_response["passport"]
    evidence = _find_evidence_link(passport, str(evidence_id))
    if evidence is None:
        return FalconEvidenceOpenBoundaryResponse(
            status="evidence_not_found",
            tenant_id=tenant_id,
            order_id=order_id,
            user_id=user_id,
            passport_id=passport_id,
            evidence_id=evidence_id,
            error={
                "code": "evidence_not_found",
                "message": "Evidence link does not belong to the synthetic data passport.",
            },
        ).to_dict()

    evidence_summary = _evidence_summary(evidence)
    role = request_payload.get("actor_role")
    if role is not None:
        permission = can_open_evidence_link(str(role), evidence_summary["access_level"])
        if not permission.allowed:
            return FalconEvidenceOpenBoundaryResponse(
                status="permission_denied",
                tenant_id=tenant_id,
                order_id=order_id,
                user_id=user_id,
                passport_id=passport_id,
                evidence_id=evidence_id,
                reason_code=permission.reason_code,
                reason_label=permission.reason_label,
            ).to_dict()

    audit_event = build_evidence_opened_event(
        tenant_id=str(tenant_id),
        order_id=str(order_id),
        user_id=str(user_id),
        match_id=str(passport_id),
        metadata={
            "detail_type": "evidence_link",
            "passport_id": passport_id,
            "fact_id": passport["fact_id"],
            "evidence_id": evidence_id,
            "source_document_type": evidence_summary["source_document_type"],
            "access_level": evidence_summary["access_level"],
            "status": evidence_summary["status"],
        },
    ).to_dict()
    return FalconEvidenceOpenBoundaryResponse(
        status="ok",
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        passport_id=passport_id,
        evidence_id=evidence_id,
        evidence_summary=evidence_summary,
        suggested_audit_event=audit_event,
    ).to_dict()


def _find_evidence_link(passport: dict[str, Any], evidence_id: str) -> dict[str, Any] | None:
    for evidence in passport.get("evidence_links", []):
        if evidence.get("evidence_id") == evidence_id:
            return evidence
    return None


def _evidence_summary(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": str(evidence["evidence_id"]),
        "source_document_id": str(evidence["source_document_id"]),
        "source_document_type": str(evidence["source_document_type"]),
        "display_label": str(evidence["display_label"]),
        "access_level": str(evidence["access_level"]),
        "status": str(evidence["status"]),
        "has_future_anchor": bool(
            evidence.get("future_page_number")
            or evidence.get("future_section_anchor")
            or evidence.get("future_highlight_text")
        ),
    }


def _optional_str(value: Any | None) -> str | None:
    if value is None or value == "":
        return None
    return str(value)
