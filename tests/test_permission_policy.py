from falcon_intel.evidence_link import EvidenceAccessLevel
from falcon_intel.permission_policy import (
    FALCON_ROLE_CODES,
    FalconRoleCode,
    PermissionActionCode,
    can_archive_fact,
    can_open_evidence_link,
    can_override_fact,
    can_review_fact,
    can_verify_fact,
    can_view_intelligence_card,
    can_view_passport_detail,
    evaluate_permission,
)


def test_role_codes_are_stable() -> None:
    assert list(FALCON_ROLE_CODES) == [
        "owner",
        "admin",
        "appraiser",
        "reviewer",
        "trainee",
        "client",
    ]


def test_client_role_cannot_access_internal_intelligence() -> None:
    decisions = [
        can_view_intelligence_card(FalconRoleCode.CLIENT),
        can_view_passport_detail(FalconRoleCode.CLIENT),
        can_open_evidence_link(FalconRoleCode.CLIENT, EvidenceAccessLevel.INTERNAL_ONLY),
        can_verify_fact(FalconRoleCode.CLIENT),
        can_review_fact(FalconRoleCode.CLIENT),
        can_override_fact(FalconRoleCode.CLIENT),
        can_archive_fact(FalconRoleCode.CLIENT),
    ]

    assert all(decision.allowed is False for decision in decisions)
    assert {decision.reason_code for decision in decisions} == {"denied_client_role"}


def test_card_and_passport_detail_visibility_by_internal_role() -> None:
    assert can_view_intelligence_card(FalconRoleCode.APPRAISER).to_dict() == {
        "allowed": True,
        "reason_code": "allowed_internal_role",
        "reason_label": "Allowed for internal Falcon Intelligence role.",
    }
    assert can_view_intelligence_card(FalconRoleCode.TRAINEE).allowed is True
    assert can_view_passport_detail(FalconRoleCode.TRAINEE).to_dict() == {
        "allowed": False,
        "reason_code": "denied_trainee_restricted",
        "reason_label": "Trainee role is restricted for this action.",
    }


def test_evidence_access_levels_are_respected() -> None:
    assert can_open_evidence_link(FalconRoleCode.APPRAISER, "internal_only").allowed is True
    assert can_open_evidence_link(FalconRoleCode.TRAINEE, "internal_only").reason_code == "denied_trainee_restricted"
    assert can_open_evidence_link(FalconRoleCode.APPRAISER, "appraiser_reviewer_only").allowed is True
    assert can_open_evidence_link(FalconRoleCode.TRAINEE, "appraiser_reviewer_only").reason_code == "denied_review_required"
    assert can_open_evidence_link(FalconRoleCode.ADMIN, "owner_admin_only").allowed is True
    assert can_open_evidence_link(FalconRoleCode.REVIEWER, "owner_admin_only").reason_code == "denied_admin_required"
    assert can_open_evidence_link(FalconRoleCode.OWNER, "disabled").to_dict() == {
        "allowed": False,
        "reason_code": "denied_disabled_evidence",
        "reason_label": "Evidence link access is disabled.",
    }


def test_fact_action_permissions_are_role_scoped() -> None:
    assert can_verify_fact(FalconRoleCode.APPRAISER).allowed is True
    assert can_verify_fact(FalconRoleCode.TRAINEE).reason_code == "denied_trainee_restricted"
    assert can_review_fact(FalconRoleCode.REVIEWER).allowed is True
    assert can_review_fact(FalconRoleCode.APPRAISER).reason_code == "denied_review_required"
    assert can_override_fact(FalconRoleCode.ADMIN).allowed is True
    assert can_override_fact(FalconRoleCode.APPRAISER).reason_code == "denied_review_required"
    assert can_archive_fact(FalconRoleCode.OWNER).allowed is True
    assert can_archive_fact(FalconRoleCode.REVIEWER).reason_code == "denied_admin_required"


def test_evaluate_permission_dispatches_supported_actions() -> None:
    assert evaluate_permission(
        PermissionActionCode.OPEN_EVIDENCE_LINK,
        FalconRoleCode.REVIEWER,
        evidence_access_level=EvidenceAccessLevel.APPRAISER_REVIEWER_ONLY,
    ).to_dict() == {
        "allowed": True,
        "reason_code": "allowed_review_role",
        "reason_label": "Allowed for reviewer or elevated internal role.",
    }
    assert evaluate_permission(
        PermissionActionCode.ARCHIVE_FACT,
        FalconRoleCode.ADMIN,
    ).allowed is True
    assert evaluate_permission("unsupported_action", FalconRoleCode.ADMIN).to_dict() == {
        "allowed": False,
        "reason_code": "denied_unsupported_action",
        "reason_label": "Unsupported permission action code.",
    }
    assert evaluate_permission(
        PermissionActionCode.VIEW_INTELLIGENCE_CARD,
        "unsupported_role",
    ).reason_code == "denied_unsupported_role"
