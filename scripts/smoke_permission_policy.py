"""Smoke validation for synthetic/local permission policy decisions."""

import json

from falcon_intel.evidence_link import EvidenceAccessLevel
from falcon_intel.permission_policy import (
    FalconRoleCode,
    PermissionActionCode,
    can_open_evidence_link,
    can_view_intelligence_card,
    can_view_passport_detail,
    evaluate_permission,
)


def main() -> None:
    decisions = {
        "appraiser_card": can_view_intelligence_card(FalconRoleCode.APPRAISER).to_dict(),
        "client_card": can_view_intelligence_card(FalconRoleCode.CLIENT).to_dict(),
        "reviewer_passport": can_view_passport_detail(FalconRoleCode.REVIEWER).to_dict(),
        "client_passport": can_view_passport_detail(FalconRoleCode.CLIENT).to_dict(),
        "appraiser_evidence": can_open_evidence_link(
            FalconRoleCode.APPRAISER,
            EvidenceAccessLevel.APPRAISER_REVIEWER_ONLY,
        ).to_dict(),
        "trainee_admin_evidence": can_open_evidence_link(
            FalconRoleCode.TRAINEE,
            EvidenceAccessLevel.OWNER_ADMIN_ONLY,
        ).to_dict(),
        "admin_archive": evaluate_permission(
            PermissionActionCode.ARCHIVE_FACT,
            FalconRoleCode.ADMIN,
        ).to_dict(),
    }

    assert decisions["appraiser_card"]["allowed"] is True
    assert decisions["client_card"]["allowed"] is False
    assert decisions["client_card"]["reason_code"] == "denied_client_role"
    assert decisions["reviewer_passport"]["allowed"] is True
    assert decisions["client_passport"]["allowed"] is False
    assert decisions["appraiser_evidence"]["allowed"] is True
    assert decisions["trainee_admin_evidence"]["reason_code"] == "denied_admin_required"
    assert decisions["admin_archive"]["allowed"] is True

    serialized = json.dumps(decisions).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("permission policy smoke validation passed")


if __name__ == "__main__":
    main()
