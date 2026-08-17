"""
Rescuer Role: Speed-focused with acceptable risk.
"""

from .base_role import BaseRole


class RescuerRole(BaseRole):
    """
    The Rescuer role balances speed with safety.
    Takes calculated risks to reach destinations faster.
    """

    @property
    def name(self) -> str:
        return "Rescuer"

    @property
    def weight_mode(self) -> str:
        return "balanced"

    @property
    def path_color(self) -> str:
        return "#ff8c00"  # Orange

    @property
    def description(self) -> str:
        return "Adaptive & Fast: Balances speed with safety, takes calculated risks."
