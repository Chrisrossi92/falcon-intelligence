"""Dependency-free smoke validation for the metadata-only CLI."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.cli import main


def main_smoke() -> None:
    with TemporaryDirectory() as workspace:
        workspace_path = Path(workspace)
        selected_root = workspace_path / "selected"
        reports = selected_root / "reports"
        reports.mkdir(parents=True)
        (reports / "synthetic-report.pdf").write_bytes(b"synthetic")
        (selected_root / "notes.txt").write_bytes(b"synthetic")
        (selected_root / "photo.jpg").write_bytes(b"synthetic")

        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(workspace_path)
            assert main(["scan", "--root", str(selected_root), "--label", "Synthetic Folder"]) == 0

            manifests = sorted((workspace_path / "data" / "manifests").glob("*.json"))
            assert len(manifests) == 1
            manifest_payload = json.loads(manifests[0].read_text(encoding="utf-8"))
            assert "absolute_root_path" not in manifest_payload

            assert main(["manifests"]) == 0
            assert main(["search", "--manifest", str(manifests[0]), "--name", "report"]) == 0
            assert main(["search", "--latest", "--name", "report"]) == 0
            assert main(["search", "--manifest", str(manifests[0]), "--extension", "pdf"]) == 0
            assert main(["search", "--manifest", str(manifests[0]), "--path", "reports"]) == 0
            assert main(["search", "--manifest", str(manifests[0]), "--supported-only"]) == 0
            assert main(["summary", "--manifest", str(manifests[0])]) == 0
            assert main(["summary", "--latest"]) == 0
            assert main(["discover", "--manifest", str(manifests[0])]) == 0
            assert main(["discover", "--latest"]) == 0
            assert main(
                [
                    "discover",
                    "--manifest",
                    str(manifests[0]),
                    "--label",
                    "archived-report",
                    "--min-confidence",
                    "10",
                    "--limit",
                    "1",
                ]
            ) == 0
            assert main(
                [
                    "profile",
                    "--manifest",
                    str(manifests[0]),
                    "--assignment-folder",
                    "reports",
                ]
            ) == 0
            assert main(
                [
                    "profile",
                    "--latest",
                    "--assignment-folder",
                    "reports",
                ]
            ) == 0
            assert main(
                [
                    "profile",
                    "--manifest",
                    str(manifests[0]),
                    "--assignment-folder",
                    "reports",
                    "--save",
                ]
            ) == 0
            assert main(
                [
                    "intelligence-card",
                    "--address",
                    "1000 Example Industrial Way",
                    "--city",
                    "Sampleton",
                    "--state",
                    "ST",
                    "--property-type",
                    "industrial",
                    "--building-size-sf",
                    "50000",
                    "--client",
                    "Synthetic Lender A",
                ]
            ) == 0
            try:
                main(["summary", "--manifest", str(manifests[0]), "--latest"])
            except SystemExit as error:
                assert error.code == 2
            else:
                raise AssertionError("Expected --manifest and --latest to be mutually exclusive.")
        finally:
            os.chdir(original_cwd)

    print("cli smoke validation passed")


if __name__ == "__main__":
    main_smoke()
