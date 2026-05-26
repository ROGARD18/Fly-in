from typing import List, Tuple, Dict
from src.parser import ConfigParser
from src.models import ZoneModel, ConnectionModel, DroneModel, StepType, Path
from src.models import DroneError
import heapq


class Simulation:
    def __init__(self, map: ConfigParser):
        self.map: ConfigParser = map
        self.drones: List[DroneModel] = self.init_drones()
        self.bookings: Dict[StepType, int] = {}
        self.neighbors: Dict[str, list] = {name: [] for name in self.map.zones}
        for connection in self.map.connections:
            self.neighbors[connection.zone1].append(connection.zone2)
            self.neighbors[connection.zone2].append(connection.zone1)
        self.determine_distance_to_goal()

    def init_drones(self) -> List[DroneModel]:
        nb_drones: int = self.map.nb_drones
        drones: List[DroneModel] = []

        for i in range(nb_drones):
            try:
                drone: DroneModel = DroneModel(id=i + 1)
            except DroneError as e:
                raise DroneError(f"Error initializing drone {i}: {e}")
            drones.append(drone)
        return drones

    def determine_distance_to_goal(self) -> None:
        """Dijkstra algorythm to determine the distance of
        each zone to the goal zone"""
        # print(self.map.goal_zone)

        queue: List[Tuple[int, str]] = [(0, self.map.goal_zone)]
        best_distances: Dict[str, int] = {self.map.goal_zone: 0}

        while queue:
            cur_dist, zone_name = heapq.heappop(queue)

            if cur_dist > best_distances.get(zone_name, float("inf")):
                continue

            self.map.zones[zone_name].distance = cur_dist
            if self.map.zones[zone_name].zone_type == "blocked":
                continue

            cost: int = (1 if self.map.zones[zone_name].zone_type == "normal"
                         else 2)
            new_dist: int = cur_dist + cost

            for neighbor in self.neighbors[zone_name]:
                if new_dist < best_distances.get(neighbor, float("inf")):
                    best_distances[neighbor] = new_dist
                    heapq.heappush(queue, (new_dist, neighbor))

    def _reconstruct_path(self,
                          visited: Dict[Tuple[str, int], Tuple[str, int]],
                          current: Tuple[str, int]
                          ) -> Path:
        path: Path = [current]
        while current in visited:
            current = visited[current]
            path.append(current)
        path.reverse()
        return path

    def a_star(self) -> List[Tuple[str, int]]:
        start_h = self.map.zones["start"].distance
        queue = [(start_h, 0, "start", 0)]

        visited: Dict[Tuple[str, int], Tuple[str, int]] = {}
        g_scores: Dict[Tuple[str, int], int] = {("start", 0): 0}

        while queue:
            f, g, cur_zone, cur_turn = heapq.heappop(queue)

            if cur_zone == self.map.goal_zone:
                return self._reconstruct_path(visited,
                                              (cur_zone, cur_turn))

            options = self.neighbors[cur_zone] + [cur_zone]

            for next_zone in options:
                zone_model = self.map.zones[next_zone]
                zone_type = getattr(zone_model, "zone_type", "normal")

                if zone_type == "blocked":
                    continue

                if next_zone == cur_zone:
                    cost = 1
                else:
                    cost = 2 if zone_type == "restricted" else 1

                new_turn = cur_turn + cost
                new_g = g + cost

                max_capacity = getattr(
                    zone_model, "max_drones", self.map.nb_drones)
                drones_already_there = self.bookings.get(
                    (next_zone, new_turn), 0)

                if drones_already_there >= max_capacity:
                    continue

                state = (next_zone, new_turn)
                if new_g < g_scores.get(state, float("inf")):
                    visited[state] = (cur_zone, cur_turn)
                    g_scores[state] = new_g

                    f_score = new_g + zone_model.distance
                    heapq.heappush(
                        queue, (f_score, new_g, next_zone, new_turn))

        return []

    def print_simulation_output(self) -> None:
        schedules = {}
        max_move = 0

        for drone in self.drones:
            if drone.path:
                schedules[drone.id] = {move: zone for zone, move in drone.path}
                last_move = drone.path[-1][1]
                if last_move > max_move:
                    max_move = last_move

        lap: int = 0
        for move in range(1, max_move + 1):
            line_moves = []

            for drone in self.drones:
                sched = schedules.get(drone.id, {})

                zone_now = sched.get(move)
                zone_prev = sched.get(move - 1)

                if zone_now and zone_prev and zone_now != zone_prev:
                    line_moves.append(f"D{drone.id}-{zone_now}")

                elif not zone_now and zone_prev:
                    target_zone = sched.get(move + 1)
                    if target_zone:
                        line_moves.append(f"D{drone.id}-conn_to_{target_zone}")

            if line_moves:
                print(" ".join(line_moves))
            lap = move
        print("Nombre de lap =", lap)


    def resolve_all_paths(self) -> None:

        for drone in self.drones:
            path = self.a_star()

            if path:
                drone.path = path
                for step in path:
                    self.bookings[step] = self.bookings.get(step, 0) + 1
            else:
                print(
                    f"[-] Aucun chemin possible trouvé pour"
                    " le drone {drone.id}")
        self.print_simulation_output()
