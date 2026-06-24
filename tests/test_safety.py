from falcon_intel.core import AppProfile
from falcon_intel.premium import PremiumModule
from falcon_intel.safety import is_blocked_source_path


def test_app_profile_defaults_are_safe() -> None:
    AppProfile().assert_safe_defaults()


def test_ingestion_enabled_is_rejected() -> None:
    try:
        AppProfile(ingestion_enabled=True).assert_safe_defaults()
    except ValueError as error:
        assert "ingestion" in str(error).lower()
    else:
        raise AssertionError("Expected ingestion-enabled profile to fail.")


def test_blocks_report_like_paths() -> None:
    assert is_blocked_source_path("reports/example.pdf")
    assert is_blocked_source_path("source_documents/export.docx")
    assert is_blocked_source_path("source-documents/export.docx")
    assert is_blocked_source_path("extracted_text/report.txt")


def test_allows_framework_paths() -> None:
    assert not is_blocked_source_path("src/falcon_intel/core.py")
    assert not is_blocked_source_path("docs/safety.md")


def test_premium_module_defaults_disabled() -> None:
    try:
        PremiumModule().require_enabled()
    except RuntimeError as error:
        assert "premium" in str(error).lower()
    else:
        raise AssertionError("Expected disabled premium module to fail.")
