"""
Base class for all role types in the simulation.
Each role defines a unique pathfinding strategy.
"""

from abc import ABC, abstractmethod


class BaseRole(ABC):
    """Abstract base class for simulation roles."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the role."""
        pass

    @property
    @abstractmethod
    def weight_mode(self) -> str:
        """Pathfinding weight mode: 'safe', 'balanced', or 'fast'."""
        pass

    @property
    @abstractmethod
    def path_color(self) -> str:
        """Hex color for path visualization."""
        pass

    @property
    def description(self) -> str:
        """Short description of the role's behavior."""
        return ""

    def decide_path(self, G, start, end, pathfinder_func, blocked_zones=None):
        """
        Calculate the optimal path for this role.

        Args:
            G: NetworkX graph
            start: Start node ID
            end: End node ID
            pathfinder_func: The A* pathfinding function
            blocked_zones: List of (lat, lon, radius, name) zones to avoid

        Returns:
            tuple: (path_nodes, path_coords)
        """
        return pathfinder_func(G, start, end, weight_mode=self.weight_mode)
