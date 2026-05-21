from typing import List, Tuple, Dict
from src.parser import ConfigParser
from src.models import ZoneModel, ConnectionModel, DroneModel, StepType
import heapq


class Simulation:
    def __init__(self, map: ConfigParser):
        self.map = map
        self.bookings: Dict[StepType, int] = {}
        self.determine_distance_to_goal()

    def valid_move(self, step: StepType) -> bool:
        zone, _ = step
        return (
            self.bookings.get(step, -1) < self.map.zones[zone].max_capacity
            )

    def determine_distance_to_goal(self) -> None:

        neighbors: Dict[str, list] = {name: [] for name in self.map.zones}
        for connection in self.map.connections:
            z1 = connection.zone1
            z2 = connection.zone2
            neighbors[z1].append(z2)
            neighbors[z2].append(z1)

        queue: List[Tuple[int, str]] = [(0, "goal")]
        best_distances: Dict[str, int] = {"goal": 0}

        while queue:
            cur_dist, zone = heapq.heappop(queue)

            if cur_dist > best_distances.get(zone, float("inf")):
                continue

            self.map.zones[zone].distance = cur_dist
            zone_type = self.map.zones[zone].zone_type
            if zone_type == "blocked":
                continue
            cost: int = 1 if zone_type == "normal" else 2
            new_dist: int = cur_dist + cost

            for neighbor in neighbors[zone]:
                if new_dist < best_distances.get(neighbor, float("inf")):
                    best_distances[neighbor] = new_dist
                    heapq.heappush(queue, (new_dist, neighbor))
