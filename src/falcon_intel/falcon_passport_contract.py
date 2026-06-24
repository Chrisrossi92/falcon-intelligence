"""Local in-memory contract boundary for future Falcon passport detail API/RPC."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from falcon_intel.audit import build_evidence_opened_event
from falcon_intel.data_passport_lookup import (
    DEFAULT_DATA_PASSPORT_FIXTURE_PATH,
    lookup_data_passport_detail,
)
from falcon_intel.schema_registry import FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION


REQUIRED_PASSPORT_DETAIL_FIELDS = (
    "tenant_id",
    "order_id",
    "user_id",
    "passport_id",
)


@dataclass(frozen=True)
class FalconPassportDetailBoundaryResponse:
    """In-memory stand-in for a future Falcon passport detail API/RPC response."""

    status: str
    tenant_id: str | None
    order_id: str | None
    user_id: str | None
    passport_id: str | None
    schema_version: str = FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION
    passport: dict[str, Any] | None = None
    suggested_audit_event: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "tenant_id": self.tenant_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "passport_id": self.passport_id,
            "schema_version": self.schema_version,
        }
        if self.passport is not None:
            payload["passport"] = self.passport
        if self.suggested_audit_event is not None:
            payload["suggested_audit_event"] = self.suggested_audit_event
        if self.error is not None:
            payload["error"] = self.error
        return payload


def build_falcon_passport_detail_response(
    request_payload: dict[str, Any],
    *,
    synthetic_passport_path: str | Path = DEFAULT_DATA_PASSPORT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Return full synthetic passport detail for a Falcon-style detail request."""

    missing_fields = [
        field
        for field in REQUIRED_PASSPORT_DETAIL_FIELDS
        if field not in request_payload or request_payload[field] in (None, "")
    ]
    tenant_id = _optional_str(request_payload.get("tenant_id"))
    order_id = _optional_str(request_payload.get("order_id"))
    user_id = _optional_str(request_payload.get("user_id"))
    passport_id = _optional_str(request_payload.get("passport_id"))
    if missing_fields:
        return FalconPassportDetailBoundaryResponse(
            status="missing_required_input",
            tenant_id=tenant_id,
            order_id=order_id,
            user_id=user_id,
            passport_id=passport_id,
            error={
                "code": "missing_required_input",
                "message": "Falcon passport detail payload is missing required fields.",
                "missing_fields": missing_fields,
            },
        ).to_dict()

    lookup_response = lookup_data_passport_detail(
        tenant_id=str(tenant_id),
        passport_id=str(passport_id),
        fixture_path=synthetic_passport_path,
    ).to_dict()
    if lookup_response["status"] != "found":
        return FalconPassportDetailBoundaryResponse(
            status="not_found",
            tenant_id=tenant_id,
            order_id=order_id,
            user_id=user_id,
            passport_id=passport_id,
            error={
                "code": "passport_not_found",
                "message": "No synthetic data passport found for tenant and passport_id.",
            },
        ).to_dict()

    passport = lookup_response["passport"]
    audit_event = build_evidence_opened_event(
        tenant_id=str(tenant_id),
        order_id=str(order_id),
        user_id=str(user_id),
        match_id=str(passport_id),
        metadata={
            "detail_type": "data_passport",
            "passport_id": passport_id,
            "fact_id": passport["fact_id"],
            "evidence_link_count": len(passport["evidence_links"]),
            "searchable_status": passport["searchable_status"],
        },
    ).to_dict()
    return FalconPassportDetailBoundaryResponse(
        status="ok",
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        passport_id=passport_id,
        passport=passport,
        suggested_audit_event=audit_event,
    ).to_dict()


def _optional_str(value: Any | None) -> str | None:
    if value is None or value == "":
        return None
    return str(value)
