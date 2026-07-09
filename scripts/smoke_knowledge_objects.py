"""Smoke validation for the local Knowledge Object Builder V1."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.knowledge_objects import (
    KnowledgeObjectsReport,
    build_report_knowledge_objects,
    save_knowledge_object_outputs,
)
from falcon_intel.verification_engine import VerificationReport, verify_report_candidate


def _candidate() -> dict[str, object]:
    return {
        "file_id": "synthetic-final",
        "file_name": "Restricted Appraisal Report.pdf",
        "file_path": "synthetic/Restricted Appraisal Report.pdf",
        "fields": {
            "report_title": [{"value": "Restricted Appraisal Report", "confidence": "medium", "source_hint": "page 1"}],
            "property_address": [{"value": "100 Sample Industrial Avenue", "confidence": "high", "source_hint": "page 1"}],
            "client": [{"value": "Example Bank", "confidence": "high", "source_hint": "page 1"}],
            "intended_user": [{"value": "Example Bank", "confidence": "high", "source_hint": "page 1"}],
            "effective_date": [{"value": "June 1, 2026", "confidence": "high", "source_hint": "page 1"}],
            "appraiser_name": [{"value": "Synthetic Appraiser", "confidence": "high", "source_hint": "certification"}],
        },
        "approaches_referenced": {},
        "sections_detected": {},
        "warnings": [],
    }


def main() -> int:
    report_facts = verify_report_candidate(_candidate(), timestamp="2026-06-30T00:00:00+00:00")
    verification_report = VerificationReport(
        verification_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_knowledge_path="synthetic-knowledge.json",
        report_facts=(report_facts,),
    )
    knowledge_package = build_report_knowledge_objects(verification_report.to_dict()["report_facts"][0])
    objects = {item.object_type: item for item in knowledge_package.object_candidates}

    assert set(objects) == {"client_user", "open_issues", "personnel", "property", "report"}
    assert objects["property"].readiness == "needs_review"
    assert objects["report"].readiness == "needs_review"
    assert objects["client_user"].readiness == "needs_review"
    assert objects["personnel"].readiness == "needs_review"
    assert objects["open_issues"].readiness == "needs_review"
    assert objects["property"].review_required_fields == ("property_address",)

    missing_only = build_report_knowledge_objects(
        {
            "file_id": "synthetic-missing",
            "file_name": "Synthetic Missing Fields.pdf",
            "file_path": "synthetic/Synthetic Missing Fields.pdf",
            "facts": [
                {
                    "field_name": "property_address",
                    "verified_value": None,
                    "verification_status": "missing",
                    "confidence": "missing",
                    "supporting_evidence": [],
                    "conflicting_evidence": [],
                    "verification_method": "synthetic missing rule",
                    "verification_timestamp": "2026-06-30T00:00:00+00:00",
                    "notes": [],
                    "source_references": [],
                }
            ],
            "warnings": [],
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    assert not missing_only.object_candidates

    blocked_package = build_report_knowledge_objects(
        {
            "file_id": "synthetic-conflict",
            "file_name": "Synthetic Conflict.pdf",
            "file_path": "synthetic/Synthetic Conflict.pdf",
            "facts": [
                {
                    "field_name": "property_address",
                    "verified_value": None,
                    "verification_status": "conflicting",
                    "confidence": "conflicting",
                    "supporting_evidence": [],
                    "conflicting_evidence": [],
                    "verification_method": "synthetic conflict rule",
                    "verification_timestamp": "2026-06-30T00:00:00+00:00",
                    "notes": [],
                    "source_references": ["synthetic-conflict:property_address:1"],
                }
            ],
            "warnings": [],
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    blocked_objects = {item.object_type: item for item in blocked_package.object_candidates}
    assert blocked_objects["property"].readiness == "blocked"
    assert blocked_objects["property"].readiness_reason == "blocked_by_conflict"

    with TemporaryDirectory() as directory:
        outputs = save_knowledge_object_outputs(
            report=KnowledgeObjectsReport(
                knowledge_object_version="1",
                generated_at="2026-06-30T00:00:00+00:00",
                source_verification_path="synthetic-verification.json",
                reports=(knowledge_package,),
            ),
            output_directory=Path(directory),
        )
        assert Path(outputs["json"]).exists()
        assert Path(outputs["markdown"]).exists()

    print("knowledge objects smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
