"""Role package initialization."""

from .base_role import BaseRole
from .army import ArmyRole
from .rescuer import RescuerRole
from .volunteer import VolunteerRole

__all__ = ["BaseRole", "ArmyRole", "RescuerRole", "VolunteerRole"]
