"""Core framework types for Falcon Intelligence."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppProfile:
    """Describes the local-first application boundary."""

    name: str = "Falcon Intelligence"
    local_first: bool = True
    ingestion_enabled: bool = False

    def assert_safe_defaults(self) -> None:
        if not self.local_first:
            raise ValueError("Falcon Intelligence must default to local-first operation.")
        if self.ingestion_enabled:
            raise ValueError("Document ingestion is disabled in the initial scaffold.")
