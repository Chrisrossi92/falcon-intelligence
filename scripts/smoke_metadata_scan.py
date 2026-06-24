"""Dependency-free smoke validation for metadata-only scanning."""

import builtins
from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.scanner import scan_metadata


def main() -> None:
    with TemporaryDirectory() as workspace:
        root = Path(workspace) / "selected"
        nested = root / "nested"
        nested.mkdir(parents=True)
        (nested / "synthetic.pdf").write_bytes(b"synthetic")
        (root / "synthetic.jpg").write_bytes(b"synthetic")

        original_open = builtins.open

        def fail_open(*args: object, **kwargs: object) -> object:
            raise AssertionError("scanner must not open file contents")

        builtins.open = fail_open
        try:
            results = scan_metadata(root)
        finally:
            builtins.open = original_open

        assert [item.relative_path for item in results] == [
            "nested/synthetic.pdf",
            "synthetic.jpg",
        ]
        assert results[0].supported_for_future_indexing is True
        assert results[1].supported_for_future_indexing is False
        assert not hasattr(results[0], "text")

    print("metadata scanner smoke validation passed")


if __name__ == "__main__":
    main()
