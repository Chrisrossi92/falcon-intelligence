"""Synthetic/local data passport detail lookup for future UI drawers."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json

from falcon_intel.data_passport import build_data_passport


DEFAULT_DATA_PASSPORT_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)


@dataclass(frozen=True)
class DataPassportLookupResponse:
    """Safe local response for data passport detail lookup."""

    status: str
    tenant_id: str
    passport_id: str
    passport: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.passport is None:
            payload.pop("passport")
        if self.error is None:
            payload.pop("error")
        return payload


def lookup_data_passport_detail(
    *,
    tenant_id: str,
    passport_id: str,
    fixture_path: str | Path = DEFAULT_DATA_PASSPORT_FIXTURE_PATH,
) -> DataPassportLookupResponse:
    """Resolve a synthetic card passport ID to full passport detail."""

    try:
        _require_non_empty("tenant_id", tenant_id)
        _require_non_empty("passport_id", passport_id)
        fixture = load_synthetic_data_passports(fixture_path)
        for record in fixture.get("passports", []):
            if record.get("passport_id") != passport_id:
                continue
            if record.get("tenant_id") != tenant_id:
                return DataPassportLookupResponse(
                    status="not_found",
                    tenant_id=tenant_id,
                    passport_id=passport_id,
                    error="No synthetic data passport found for tenant and passport_id.",
                )
            return DataPassportLookupResponse(
                status="found",
                tenant_id=tenant_id,
                passport_id=passport_id,
                passport=_validated_passport_record(record),
            )
        return DataPassportLookupResponse(
            status="not_found",
            tenant_id=tenant_id,
            passport_id=passport_id,
            error="No synthetic data passport found for tenant and passport_id.",
        )
    except Exception as error:
        return DataPassportLookupResponse(
            status="error",
            tenant_id=str(tenant_id),
            passport_id=str(passport_id),
            error=str(error),
        )


def load_synthetic_data_passports(path: str | Path = DEFAULT_DATA_PASSPORT_FIXTURE_PATH) -> dict[str, Any]:
    """Load and validate the committed synthetic data passport detail fixture."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _validate_synthetic_data_passport_fixture(payload)
    return payload


def _validate_synthetic_data_passport_fixture(payload: dict[str, Any]) -> None:
    if payload.get("fixture_kind") != "synthetic_data_passports":
        raise ValueError("Data passport lookup requires a synthetic data passport fixture.")
    if _contains_prohibited_source_content(payload):
        raise ValueError("Synthetic data passport fixture contains prohibited source-content fields.")
    for record in payload.get("passports", []):
        _validated_passport_record(record)


def _validated_passport_record(record: dict[str, Any]) -> dict[str, Any]:
    _require_non_empty("passport_id", record.get("passport_id"))
    passport = build_data_passport(
        fact_id=str(record["fact_id"]),
        tenant_id=str(record["tenant_id"]),
        assignment_id=str(record["assignment_id"]),
        fact_type=str(record["fact_type"]),
        display_label=str(record["display_label"]),
        display_value=str(record["display_value"]),
        verification_status=str(record["verification_status"]),
        verified_by=str(record["verified_by"]),
        verified_at=str(record["verified_at"]),
        reviewed_by=record.get("reviewed_by"),
        reviewed_at=record.get("reviewed_at"),
        confidence_dimensions=record["confidence_dimensions"],
        evidence_links=record["evidence_links"],
        audit_event_ids=record.get("audit_event_ids", []),
        searchable_status=str(record["searchable_status"]),
    ).to_dict()
    return {"passport_id": str(record["passport_id"]), **passport}


def _contains_prohibited_source_content(value: Any) -> bool:
    prohibited_keys = {"report_text", "source_file_path", "absolute_path", "onedrive_path"}
    if isinstance(value, dict):
        return any(
            str(key).lower() in prohibited_keys or _contains_prohibited_source_content(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_prohibited_source_content(item) for item in value)
    if isinstance(value, str):
        return "onedrive" in value.lower()
    return False


def _require_non_empty(field_name: str, value: Any | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")
