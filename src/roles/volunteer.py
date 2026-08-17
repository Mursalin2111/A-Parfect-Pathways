"""
Volunteer Role: Balanced efficiency, avoids high-cost edges.
"""

from .base_role import BaseRole


class VolunteerRole(BaseRole):
    """
    The Volunteer role seeks efficient routes.
    Avoids paths with high resource costs.
    """

    @property
    def name(self) -> str:
        return "Volunteer"

    @property
    def weight_mode(self) -> str:
        return "efficient"

    @property
    def path_color(self) -> str:
        return "#007bff"  # Blue

    @property
    def description(self) -> str:
        return "Balanced & Efficient: Seeks middle-ground paths, avoids resource-heavy routes."
