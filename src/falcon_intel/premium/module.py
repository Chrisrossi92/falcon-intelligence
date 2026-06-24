"""Placeholder contract for future premium capabilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PremiumModule:
    """Represents a disabled premium extension point."""

    enabled: bool = False

    def require_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("Falcon premium features are not enabled in this scaffold.")
