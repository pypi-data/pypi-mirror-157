"""Blade information."""
from __future__ import annotations

from .landroid_class import LDict


class Blades(LDict):
    """Blade information."""

    def __init__(
        self,
        data=None,
    ) -> None:
        """Initialize blade object."""
        super().__init__()
        from ..helpers import string_to_time

        if isinstance(data, type(None)):
            return

        if "blade_work_time" in data:
            # Total time with blades on in minutes
            self["total_on"] = int(data["blade_work_time"])
        else:
            self["total_on"] = None

        if "blade_work_time_reset" in data:
            # Blade time reset at minutes
            self["reset_at"] = int(data["blade_work_time_reset"])
        else:
            self["reset_at"] = None

        if "blade_work_time_reset_at" in data:
            # Blade time reset time and date
            self["reset_time"] = (
                string_to_time(data["blade_work_time_reset_at"], data["time_zone"])
                if not isinstance(data["blade_work_time_reset_at"], type(None))
                else None
            )
        else:
            self["reset_time"] = None

        # Calculate blade data since reset, if possible
        if self["reset_at"] and self["total_on"]:
            # Blade time since last reset
            self["current_on"] = int(self["total_on"] - self["reset_at"])
        else:
            self["current_on"] = self["total_on"]
