from typing import List, Tuple, Dict
from src.parser import ConfigParser
from src.models import ZoneModel, ConnectionModel, DroneModel, StepType
import heapq


class Simulation:
    def __init__(self, map: ConfigParser):
        self.map = map
        self.bookings: Dict[StepType, int] = {}

    def valid_move(self, step: StepType) -> bool:
        zone, _ = step
        return (
            self.bookings.get(step, -1) < self.map.zones[zone].max_capacity
            )

    def determine_distance_to_goal(self) -> None:
        check_zones: list[str] = []
        new_zones: list[str] = []
        lap: int = 1

        for connecion in self.map.connections:
            zone1 = self.map.zones[connecion.zone1]
            zone2 = self.map.zones[connecion.zone2]
            # zone1.neighbors.append(zone2.name)
            # zone2.neighbors.append(zone1.name)
            if zone2.name == "goal":
                new_zones.append(zone1.name)
                zone1.distance = lap
            elif zone2.name in check_zones:
                new_zones.append(zone1.name)
                zone1.distance = lap
            lap += 1
