"""Synthetic subject profile and report field registry workflows."""

from dataclasses import asdict, dataclass, replace
from typing import Any, Literal


ReportFieldStatus = Literal["missing", "needs_review", "approved", "locked"]


FIELD_STATUSES: tuple[ReportFieldStatus, ...] = (
    "missing",
    "needs_review",
    "approved",
    "locked",
)


@dataclass(frozen=True)
class ReportField:
    """One controlled field that can later support report assembly."""

    key: str
    label: str
    value: str | int | float | None
    source: str
    confidence: int
    status: ReportFieldStatus
    notes: str
    used_in_report_count: int

    def __post_init__(self) -> None:
        if "." not in self.key:
            raise ValueError("Report field keys must use dot notation.")
        if self.confidence < 0 or self.confidence > 100:
            raise ValueError("Field confidence must be between 0 and 100.")
        if self.status not in FIELD_STATUSES:
            raise ValueError(f"Unsupported field status: {self.status}")
        if self.used_in_report_count < 0:
            raise ValueError("used_in_report_count must be zero or greater.")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["usedInReportCount"] = payload.pop("used_in_report_count")
        return payload


@dataclass(frozen=True)
class SubjectProfileSection:
    """Appraiser-facing grouping for field review."""

    title: str
    field_keys: tuple[str, ...]

    def to_dict(self, registry: dict[str, ReportField]) -> dict[str, Any]:
        return {
            "title": self.title,
            "fields": [registry[key].to_dict() for key in self.field_keys],
        }


@dataclass(frozen=True)
class SubjectProfile:
    """Structured subject profile view model backed by a report field registry."""

    subject_label: str
    registry: dict[str, ReportField]
    sections: tuple[SubjectProfileSection, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject_label,
            "readiness": subject_profile_readiness(self),
            "sections": [section.to_dict(self.registry) for section in self.sections],
            "openVerificationItems": [
                field.to_dict()
                for field in self.registry.values()
                if field.status in {"missing", "needs_review"}
            ],
            "narrativeThemes": [
                field.to_dict()
                for field in self.registry.values()
                if field.key.startswith("narrative.")
            ],
        }


def build_demo_subject_profile(
    *,
    approve: tuple[str, ...] = (),
    lock: tuple[str, ...] = (),
) -> SubjectProfile:
    """Build the synthetic 517 E Riverview Avenue profile preview."""

    profile = SubjectProfile(
        subject_label="517 E Riverview Avenue",
        registry=_demo_registry(),
        sections=_subject_profile_sections(),
    )
    if approve:
        profile = approve_report_fields(profile, approve)
    if lock:
        profile = lock_report_fields(profile, lock)
    return profile


def approve_report_fields(profile: SubjectProfile, field_keys: tuple[str, ...]) -> SubjectProfile:
    """Return a profile with selected value-bearing fields marked approved."""

    return _update_field_status(profile, field_keys, "approved")


def lock_report_fields(profile: SubjectProfile, field_keys: tuple[str, ...]) -> SubjectProfile:
    """Return a profile with selected value-bearing fields marked locked."""

    return _update_field_status(profile, field_keys, "locked")


def subject_profile_readiness(profile: SubjectProfile) -> dict[str, Any]:
    """Calculate completion and report merge readiness from registry statuses."""

    fields = tuple(profile.registry.values())
    report_fields = tuple(field for field in fields if field.used_in_report_count > 0)
    value_present_count = sum(1 for field in fields if field.status != "missing")
    approved_or_locked_count = sum(1 for field in fields if field.status in {"approved", "locked"})
    ready_report_count = sum(
        1 for field in report_fields if field.status in {"approved", "locked"}
    )
    missing_count = sum(1 for field in fields if field.status == "missing")
    needs_review_count = sum(1 for field in fields if field.status == "needs_review")
    locked_count = sum(1 for field in fields if field.status == "locked")

    return {
        "totalFields": len(fields),
        "completionPercentage": _percentage(value_present_count, len(fields)),
        "approvedOrLockedPercentage": _percentage(approved_or_locked_count, len(fields)),
        "reportMergeReadinessPercentage": _percentage(ready_report_count, len(report_fields)),
        "reportMergeReadiness": _readiness_label(ready_report_count, len(report_fields)),
        "missingCount": missing_count,
        "needsReviewCount": needs_review_count,
        "lockedCount": locked_count,
        "requiredReportFieldCount": len(report_fields),
    }


def _update_field_status(
    profile: SubjectProfile,
    field_keys: tuple[str, ...],
    status: ReportFieldStatus,
) -> SubjectProfile:
    registry = dict(profile.registry)
    for key in field_keys:
        if key not in registry:
            raise ValueError(f"Unknown report field: {key}")
        field = registry[key]
        if field.value in {None, ""}:
            raise ValueError(f"Cannot mark missing field as {status}: {key}")
        registry[key] = replace(field, status=status)
    return replace(profile, registry=registry)


def _percentage(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return 100
    return round((numerator / denominator) * 100)


def _readiness_label(ready_count: int, total_count: int) -> str:
    if total_count == 0:
        return "ready"
    percentage = ready_count / total_count
    if percentage == 1:
        return "ready"
    if percentage >= 0.75:
        return "nearly_ready"
    if percentage >= 0.5:
        return "partial"
    return "blocked"


def _field(
    key: str,
    label: str,
    value: str | int | float | None,
    source: str,
    confidence: int,
    status: ReportFieldStatus,
    notes: str,
    used_in_report_count: int,
) -> ReportField:
    return ReportField(
        key=key,
        label=label,
        value=value,
        source=source,
        confidence=confidence,
        status=status,
        notes=notes,
        used_in_report_count=used_in_report_count,
    )


def _demo_registry() -> dict[str, ReportField]:
    fields = [
        _field(
            "client.name",
            "Client",
            "Continental Demo Lending",
            "Synthetic order intake",
            92,
            "approved",
            "Demo client for workflow preview.",
            3,
        ),
        _field(
            "assignment.intended_use",
            "Intended Use",
            "Mortgage financing",
            "Synthetic engagement summary",
            90,
            "approved",
            "Confirm final wording before report merge.",
            4,
        ),
        _field(
            "assignment.property_rights",
            "Property Rights",
            "Fee simple",
            "Synthetic engagement summary",
            85,
            "needs_review",
            "Needs appraiser confirmation.",
            5,
        ),
        _field(
            "assignment.value_condition",
            "Value Condition",
            "As is",
            "Synthetic assignment setup",
            88,
            "approved",
            "No prospective condition modeled in this demo.",
            4,
        ),
        _field(
            "ownership.owner_name",
            "Current Owner",
            "Riverview Holdings Demo LLC",
            "Synthetic public record note",
            74,
            "needs_review",
            "Verify vesting before final report use.",
            2,
        ),
        _field(
            "transaction.purchase_price",
            "Purchase Price",
            425000,
            "Synthetic purchase contract summary",
            76,
            "needs_review",
            "Needs source confirmation and contract date.",
            4,
        ),
        _field(
            "subject.address",
            "Address",
            "517 E Riverview Avenue",
            "Synthetic order intake",
            96,
            "locked",
            "Locked as the profile anchor field.",
            8,
        ),
        _field(
            "subject.city",
            "City",
            "Dayton",
            "Synthetic order intake",
            94,
            "approved",
            "City used for jurisdiction routing.",
            5,
        ),
        _field(
            "subject.county",
            "County",
            "Montgomery County",
            "Synthetic public record note",
            82,
            "needs_review",
            "Confirm county and taxing district.",
            4,
        ),
        _field(
            "subject.state",
            "State",
            "OH",
            "Synthetic order intake",
            96,
            "approved",
            "State abbreviation normalized.",
            5,
        ),
        _field(
            "subject.parcel_number",
            "Parcel Number",
            None,
            "Synthetic assessor lookup placeholder",
            0,
            "missing",
            "Parcel number has not been entered.",
            6,
        ),
        _field(
            "site.size_acres",
            "Site Size",
            0.42,
            "Synthetic assessor note",
            68,
            "needs_review",
            "Verify against survey or assessor record.",
            5,
        ),
        _field(
            "site.flood_zone",
            "Flood Zone",
            "X",
            "Synthetic flood map note",
            70,
            "needs_review",
            "Map panel and effective date still needed.",
            3,
        ),
        _field(
            "improvements.gba_sf",
            "Gross Building Area",
            6120,
            "Synthetic inspection sketch",
            72,
            "needs_review",
            "Measurement basis needs appraiser review.",
            6,
        ),
        _field(
            "improvements.year_built",
            "Year Built",
            1987,
            "Synthetic assessor note",
            78,
            "needs_review",
            "Verify if renovation history changes effective age.",
            4,
        ),
        _field(
            "improvements.condition",
            "Condition",
            "Average",
            "Synthetic inspection observation",
            80,
            "needs_review",
            "Confirm after photo review.",
            5,
        ),
        _field(
            "zoning.code",
            "Zoning Code",
            "NC",
            "Synthetic zoning lookup",
            66,
            "needs_review",
            "Confirm local district label.",
            5,
        ),
        _field(
            "zoning.source",
            "Zoning Source",
            None,
            "Synthetic zoning lookup placeholder",
            0,
            "missing",
            "Source citation is still open.",
            2,
        ),
        _field(
            "assessment.land_value",
            "Assessed Land Value",
            38500,
            "Synthetic assessor note",
            63,
            "needs_review",
            "Tax year not confirmed.",
            1,
        ),
        _field(
            "assessment.improvement_value",
            "Assessed Improvement Value",
            214200,
            "Synthetic assessor note",
            63,
            "needs_review",
            "Tax year not confirmed.",
            1,
        ),
        _field(
            "tax.annual_amount",
            "Annual Taxes",
            None,
            "Synthetic tax lookup placeholder",
            0,
            "missing",
            "Annual tax amount needs entry.",
            2,
        ),
        _field(
            "inspection.exterior_observations",
            "Exterior Observations",
            "Brick exterior; paved surface parking; visible deferred maintenance at rear entry.",
            "Synthetic photo observation",
            60,
            "needs_review",
            "Observation is a placeholder for UI workflow only.",
            2,
        ),
        _field(
            "occupancy.status",
            "Occupancy Status",
            "Partially occupied",
            "Synthetic inspection observation",
            70,
            "needs_review",
            "Confirm current rent roll or inspection notes.",
            4,
        ),
        _field(
            "occupancy.current_user",
            "Current User",
            "Owner-user plus one small tenant",
            "Synthetic inspection observation",
            64,
            "needs_review",
            "Lease details are intentionally not modeled yet.",
            2,
        ),
        _field(
            "verification.open_items",
            "Open Verification Items",
            "Parcel number, zoning source, tax amount, GBA support, and occupancy support.",
            "Synthetic profile rollup",
            82,
            "needs_review",
            "Generated from registry state, not source extraction.",
            0,
        ),
        _field(
            "narrative.primary_theme",
            "Primary Narrative Theme",
            "Small commercial property with verification focused on site, zoning, and occupancy support.",
            "Synthetic appraiser note",
            75,
            "needs_review",
            "Theme is not report language.",
            0,
        ),
        _field(
            "narrative.risk_theme",
            "Risk Theme",
            "Report merge should wait on parcel, zoning source, and tax fields.",
            "Synthetic appraiser note",
            82,
            "approved",
            "Used as a profile control note only.",
            0,
        ),
    ]
    return {field.key: field for field in fields}


def _subject_profile_sections() -> tuple[SubjectProfileSection, ...]:
    return (
        SubjectProfileSection(
            "Assignment Summary",
            (
                "client.name",
                "assignment.intended_use",
                "assignment.property_rights",
                "assignment.value_condition",
            ),
        ),
        SubjectProfileSection(
            "Current Ownership / Transaction",
            (
                "ownership.owner_name",
                "transaction.purchase_price",
            ),
        ),
        SubjectProfileSection(
            "Property Identification",
            (
                "subject.address",
                "subject.city",
                "subject.county",
                "subject.state",
                "subject.parcel_number",
            ),
        ),
        SubjectProfileSection(
            "Site Data",
            (
                "site.size_acres",
                "site.flood_zone",
            ),
        ),
        SubjectProfileSection(
            "Improvement Data",
            (
                "improvements.gba_sf",
                "improvements.year_built",
                "improvements.condition",
            ),
        ),
        SubjectProfileSection(
            "Zoning",
            (
                "zoning.code",
                "zoning.source",
            ),
        ),
        SubjectProfileSection(
            "Assessment / Tax Data",
            (
                "assessment.land_value",
                "assessment.improvement_value",
                "tax.annual_amount",
            ),
        ),
        SubjectProfileSection(
            "Inspection / Photo Observations",
            (
                "inspection.exterior_observations",
                "occupancy.status",
                "occupancy.current_user",
            ),
        ),
        SubjectProfileSection(
            "Open Verification Items",
            ("verification.open_items",),
        ),
        SubjectProfileSection(
            "Narrative Themes",
            (
                "narrative.primary_theme",
                "narrative.risk_theme",
            ),
        ),
    )
