"""
Army Role: Maximum safety, avoids all danger zones.
"""

from .base_role import BaseRole


class ArmyRole(BaseRole):
    """
    The Army role prioritizes safety above all else.
    Uses maximum risk penalty and avoids enemy zones entirely.
    """

    @property
    def name(self) -> str:
        return "Army"

    @property
    def weight_mode(self) -> str:
        return "safe"

    @property
    def path_color(self) -> str:
        return "#28a745"  # Green

    @property
    def description(self) -> str:
        return "Strategic & Cautious: Avoids all danger zones, prioritizes safety over speed."

    def decide_path(self, G, start, end, pathfinder_func, blocked_zones=None):
        """
        Army avoids all blocked zones by treating them as impassable.
        """
        # For now, use the standard pathfinder with 'safe' mode
        # Future: Filter edges inside blocked_zones before pathfinding
        return pathfinder_func(G, start, end, weight_mode=self.weight_mode)
