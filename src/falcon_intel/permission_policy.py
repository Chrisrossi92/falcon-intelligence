"""Synthetic/local permission policy scaffold for Falcon Intelligence."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from falcon_intel.evidence_link import EvidenceAccessLevel


class FalconRoleCode(StrEnum):
    """Stable internal role identifiers for future Falcon policy wiring."""

    OWNER = "owner"
    ADMIN = "admin"
    APPRAISER = "appraiser"
    REVIEWER = "reviewer"
    TRAINEE = "trainee"
    CLIENT = "client"


FALCON_ROLE_CODES = tuple(role.value for role in FalconRoleCode)


class PermissionActionCode(StrEnum):
    """Stable permission action identifiers for Falcon Intelligence."""

    VIEW_INTELLIGENCE_CARD = "can_view_intelligence_card"
    VIEW_PASSPORT_DETAIL = "can_view_passport_detail"
    OPEN_EVIDENCE_LINK = "can_open_evidence_link"
    VERIFY_FACT = "can_verify_fact"
    REVIEW_FACT = "can_review_fact"
    OVERRIDE_FACT = "can_override_fact"
    ARCHIVE_FACT = "can_archive_fact"


class PermissionReasonCode(StrEnum):
    """Stable reason identifiers for local permission decisions."""

    ALLOWED_INTERNAL_ROLE = "allowed_internal_role"
    ALLOWED_ASSIGNED_INTERNAL_ROLE = "allowed_assigned_internal_role"
    ALLOWED_REVIEW_ROLE = "allowed_review_role"
    ALLOWED_ADMIN_ROLE = "allowed_admin_role"
    DENIED_CLIENT_ROLE = "denied_client_role"
    DENIED_TRAINEE_RESTRICTED = "denied_trainee_restricted"
    DENIED_REVIEW_REQUIRED = "denied_review_required"
    DENIED_ADMIN_REQUIRED = "denied_admin_required"
    DENIED_DISABLED_EVIDENCE = "denied_disabled_evidence"
    DENIED_UNSUPPORTED_ROLE = "denied_unsupported_role"
    DENIED_UNSUPPORTED_ACTION = "denied_unsupported_action"


PERMISSION_REASON_LABELS = {
    PermissionReasonCode.ALLOWED_INTERNAL_ROLE: "Allowed for internal Falcon Intelligence role.",
    PermissionReasonCode.ALLOWED_ASSIGNED_INTERNAL_ROLE: "Allowed for assigned internal appraisal workflow role.",
    PermissionReasonCode.ALLOWED_REVIEW_ROLE: "Allowed for reviewer or elevated internal role.",
    PermissionReasonCode.ALLOWED_ADMIN_ROLE: "Allowed for owner or admin role.",
    PermissionReasonCode.DENIED_CLIENT_ROLE: "Client role cannot access internal Falcon Intelligence.",
    PermissionReasonCode.DENIED_TRAINEE_RESTRICTED: "Trainee role is restricted for this action.",
    PermissionReasonCode.DENIED_REVIEW_REQUIRED: "Reviewer, appraiser, admin, or owner role is required.",
    PermissionReasonCode.DENIED_ADMIN_REQUIRED: "Owner or admin role is required.",
    PermissionReasonCode.DENIED_DISABLED_EVIDENCE: "Evidence link access is disabled.",
    PermissionReasonCode.DENIED_UNSUPPORTED_ROLE: "Unsupported Falcon role code.",
    PermissionReasonCode.DENIED_UNSUPPORTED_ACTION: "Unsupported permission action code.",
}


@dataclass(frozen=True)
class PermissionDecision:
    """Synthetic/local permission decision object."""

    allowed: bool
    reason_code: str
    reason_label: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def can_view_intelligence_card(role: FalconRoleCode | str) -> PermissionDecision:
    """Decide whether a role can view the internal Firm Intelligence card."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)
    if active_role == FalconRoleCode.TRAINEE:
        return _decision(True, PermissionReasonCode.ALLOWED_ASSIGNED_INTERNAL_ROLE)
    return _decision(True, PermissionReasonCode.ALLOWED_INTERNAL_ROLE)


def can_view_passport_detail(role: FalconRoleCode | str) -> PermissionDecision:
    """Decide whether a role can view a data passport detail drawer."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)
    if active_role == FalconRoleCode.TRAINEE:
        return _decision(False, PermissionReasonCode.DENIED_TRAINEE_RESTRICTED)
    return _decision(True, PermissionReasonCode.ALLOWED_INTERNAL_ROLE)


def can_open_evidence_link(
    role: FalconRoleCode | str,
    access_level: EvidenceAccessLevel | str,
) -> PermissionDecision:
    """Decide whether a role can open a metadata-only evidence link."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)

    active_access_level = EvidenceAccessLevel(access_level)
    if active_access_level == EvidenceAccessLevel.DISABLED:
        return _decision(False, PermissionReasonCode.DENIED_DISABLED_EVIDENCE)
    if active_access_level == EvidenceAccessLevel.INTERNAL_ONLY:
        if active_role == FalconRoleCode.TRAINEE:
            return _decision(False, PermissionReasonCode.DENIED_TRAINEE_RESTRICTED)
        return _decision(True, PermissionReasonCode.ALLOWED_INTERNAL_ROLE)
    if active_access_level == EvidenceAccessLevel.APPRAISER_REVIEWER_ONLY:
        if active_role in {
            FalconRoleCode.OWNER,
            FalconRoleCode.ADMIN,
            FalconRoleCode.APPRAISER,
            FalconRoleCode.REVIEWER,
        }:
            return _decision(True, PermissionReasonCode.ALLOWED_REVIEW_ROLE)
        return _decision(False, PermissionReasonCode.DENIED_REVIEW_REQUIRED)
    if active_access_level == EvidenceAccessLevel.OWNER_ADMIN_ONLY:
        if active_role in {FalconRoleCode.OWNER, FalconRoleCode.ADMIN}:
            return _decision(True, PermissionReasonCode.ALLOWED_ADMIN_ROLE)
        return _decision(False, PermissionReasonCode.DENIED_ADMIN_REQUIRED)
    return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ACTION)


def can_verify_fact(role: FalconRoleCode | str) -> PermissionDecision:
    """Decide whether a role can verify a fact."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)
    if active_role in {
        FalconRoleCode.OWNER,
        FalconRoleCode.ADMIN,
        FalconRoleCode.APPRAISER,
        FalconRoleCode.REVIEWER,
    }:
        return _decision(True, PermissionReasonCode.ALLOWED_REVIEW_ROLE)
    return _decision(False, PermissionReasonCode.DENIED_TRAINEE_RESTRICTED)


def can_review_fact(role: FalconRoleCode | str) -> PermissionDecision:
    """Decide whether a role can review a fact."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)
    if active_role in {FalconRoleCode.OWNER, FalconRoleCode.ADMIN, FalconRoleCode.REVIEWER}:
        return _decision(True, PermissionReasonCode.ALLOWED_REVIEW_ROLE)
    return _decision(False, PermissionReasonCode.DENIED_REVIEW_REQUIRED)


def can_override_fact(role: FalconRoleCode | str) -> PermissionDecision:
    """Decide whether a role can override a fact or warning."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)
    if active_role in {FalconRoleCode.OWNER, FalconRoleCode.ADMIN, FalconRoleCode.REVIEWER}:
        return _decision(True, PermissionReasonCode.ALLOWED_REVIEW_ROLE)
    return _decision(False, PermissionReasonCode.DENIED_REVIEW_REQUIRED)


def can_archive_fact(role: FalconRoleCode | str) -> PermissionDecision:
    """Decide whether a role can archive a fact."""

    active_role = _coerce_role(role)
    if active_role is None:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ROLE)
    if active_role == FalconRoleCode.CLIENT:
        return _decision(False, PermissionReasonCode.DENIED_CLIENT_ROLE)
    if active_role in {FalconRoleCode.OWNER, FalconRoleCode.ADMIN}:
        return _decision(True, PermissionReasonCode.ALLOWED_ADMIN_ROLE)
    return _decision(False, PermissionReasonCode.DENIED_ADMIN_REQUIRED)


def evaluate_permission(
    action: PermissionActionCode | str,
    role: FalconRoleCode | str,
    *,
    evidence_access_level: EvidenceAccessLevel | str | None = None,
) -> PermissionDecision:
    """Evaluate one supported Falcon Intelligence permission action."""

    try:
        active_action = PermissionActionCode(action)
    except ValueError:
        return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ACTION)

    if active_action == PermissionActionCode.VIEW_INTELLIGENCE_CARD:
        return can_view_intelligence_card(role)
    if active_action == PermissionActionCode.VIEW_PASSPORT_DETAIL:
        return can_view_passport_detail(role)
    if active_action == PermissionActionCode.OPEN_EVIDENCE_LINK:
        if evidence_access_level is None:
            return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ACTION)
        return can_open_evidence_link(role, evidence_access_level)
    if active_action == PermissionActionCode.VERIFY_FACT:
        return can_verify_fact(role)
    if active_action == PermissionActionCode.REVIEW_FACT:
        return can_review_fact(role)
    if active_action == PermissionActionCode.OVERRIDE_FACT:
        return can_override_fact(role)
    if active_action == PermissionActionCode.ARCHIVE_FACT:
        return can_archive_fact(role)
    return _decision(False, PermissionReasonCode.DENIED_UNSUPPORTED_ACTION)


def _coerce_role(role: FalconRoleCode | str) -> FalconRoleCode | None:
    try:
        return FalconRoleCode(role)
    except ValueError:
        return None


def _decision(allowed: bool, reason_code: PermissionReasonCode) -> PermissionDecision:
    return PermissionDecision(
        allowed=allowed,
        reason_code=reason_code.value,
        reason_label=PERMISSION_REASON_LABELS[reason_code],
    )
