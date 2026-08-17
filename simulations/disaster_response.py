"""
Disaster Response Simulation
"""
from typing import Dict, List
import networkx as nx
from src.environment import Environment
from src.roles import Army, Rescuer, Volunteer


class DisasterResponseSimulation:
    """Simulate disaster response scenarios."""
    
    def __init__(self, environment: Environment):
        self.env = environment
        self.missions = []
        self.stats = {
            'people_rescued': 0,
            'supplies_delivered': 0,
            'total_distance': 0.0
        }
        
    def run_rescue_mission(self, rescuer: Rescuer, start: int, goal: int):
        """Run a rescue mission."""
        path = rescuer.make_decision(start, goal)
        
        if path:
            rescued = rescuer.count_rescues(path)
            self.stats['people_rescued'] += rescued
            self.missions.append({
                'type': 'rescue',
                'path': path,
                'rescued': rescued
            })
            
    def run_supply_mission(self, volunteer: Volunteer, start: int, goal: int):
        """Run a supply delivery mission."""
        path = volunteer.make_decision(start, goal)
        
        if path:
            efficiency = volunteer.calculate_efficiency(path)
            self.missions.append({
                'type': 'supply',
                'path': path,
                'efficiency': efficiency
            })
            
    def get_statistics(self) -> Dict:
        """Get simulation statistics."""
        return self.stats
