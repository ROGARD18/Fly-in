import re
from typing import List, Tuple, Any, Dict, Match
from src.models import ZoneModel, ConnectionModel


class MapParserError(Exception):
    pass


COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "gray": (128, 128, 128),
    "rainbow": (148, 0, 211),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gold": (255, 215, 0),
    "crimson": (220, 20, 60),
    "darkred": (139, 0, 0),
    "brown": (165, 42, 42),
    "maroon": (128, 0, 0),
}


class ConfigParser:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.nb_drones: int = 0
        self.zones: Dict[str, ZoneModel] = {}
        self.connections: List[ConnectionModel] = []
        self.parse()
        self.goal_zone: str
        self.start_zone: str

    def _parse_color(self, color_str: str) -> tuple[int, int, int]:
        color_clean = color_str.lower().strip()

        return COLOR_MAP.get(color_clean, (200, 200, 200))

    def _parse_options(self, options_str: str) -> Dict[str, Any] | None:
        options: Dict[str, Any] = {}
        if not options_str:
            return None

        options_str = options_str.strip("[]")
        pairs = re.findall(r"(\w+)(?:[=\s](\w+))?", options_str)
        for key, value in pairs:
            if not value:
                continue
            if value.isdigit():
                options[key] = int(value)
            if key == "color":
                options[key] = self._parse_color(str(value))
            else:
                options[key] = value
        return options

    def parse(self) -> Tuple[int, Dict[str, ZoneModel], List[ConnectionModel]]:
        start_count: int = 0
        end_count: int = 0
        with open(self.file_path, "r") as f:
            for line_id, line in enumerate(f, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if self.nb_drones == 0:
                    if line.startswith(("nb_drones:", "nb drones:")):
                        self.nb_drones = int(line.split(":")[1].strip())
                        continue
                    else:
                        raise MapParserError(f"Line {line_id}: Expected "
                                             "'nb_drones:' as the first line.")

                options_dict = {}
                options_match = re.search(r"\[(.*?)\]", line)

                if options_match:
                    options_dict = self._parse_options(options_match.group(1))
                    line = re.sub(r"\[.*?\]", "", line).strip()

                if line.startswith(("start_hub", "end_hub", "hub")):
                    prefix, rest = line.split(":", 1)
                    parts = rest.strip().split()

                    if prefix == "start_hub":
                        start_count += 1
                        self.start_zone = parts[0]
                    elif prefix == "end_hub":
                        end_count += 1
                        self.goal_zone = parts[0]

                    if start_count > 1 or end_count > 1:
                        raise MapParserError(
                            f"Line {line_id}: start ou end hub: multiple times")
                    if len(parts) < 3:
                        raise MapParserError(
                            f"Line {line_id}: Invalid zone definition.")

                    name, x, y = parts[0], int(parts[1]), int(parts[2])

                    if prefix in ("start_hub", "end_hub"):
                        options_dict["zone"] = "normal"

                    if "max_drones" not in options_dict:
                        options_dict["max_drones"] = self.nb_drones

                    try:
                        zone = ZoneModel(name=name, x=x, y=y, **options_dict)
                        self.zones[name] = zone
                    except Exception as e:
                        raise MapParserError(f"Line {line_id}: {str(e)}")

                elif line.startswith("connection:"):
                    _, rest = line.split(":", 1)
                    if '-' not in rest:
                        raise MapParserError(
                            f"Line {line_id}: Invalid connection definition.")

                    zones_parts = rest.strip().split('-')
                    z1, z2 = zones_parts[0].strip(), zones_parts[1].strip()

                    if z1 not in self.zones or z2 not in self.zones:
                        raise MapParserError(
                            f"Line {line_id}: Connection refers to undefined zones.")
                    try:
                        connection = ConnectionModel(
                            zone1=z1, zone2=z2, **options_dict)
                        self.connections.append(connection)
                    except Exception as e:
                        raise MapParserError(f"Line {line_id}: {str(e)}")
        return self.nb_drones, self.zones, self.connections
