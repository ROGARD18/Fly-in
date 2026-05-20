import re
from typing import List, Tuple, Any, Dict, Match
from src.models import ZoneModel, ConnectionModel


class MapParserError(Exception):
    pass


class ConfigParser:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.nb_drone: int = 0
        self.zones: Dict[str, ZoneModel] = {}
        self.connections: List[ConnectionModel] = []

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any] | None:
        metadata: Dict[str, Any] = {}
        if not metadata_str:
            return None

        metadata_str = metadata_str.strip("[]")
        pairs = re.findall(r"(\w+)(?:[=\s](\w+))?", metadata_str)
        for key, value in pairs:
            if not value:
                continue
            if value.isdigit():
                metadata[key] = int(value)
            else:
                metadata[key] = value
        return metadata

    def parse(self) -> Tuple[int, Dict[str, ZoneModel], List[ConnectionModel]]:
        with open(self.file_path, "r") as f:
            for line_id, line in enumerate(f, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if self.nb_drone == 0:
                    if line.startswith(("nb_drones:", "nb drones:")):
                        self.nb_drone = int(line.split(":")[1].strip())
                        continue
                    else:
                        raise MapParserError(f"Line {line_id}: Expected "
                                             "'nb_drones:' as the first line.")

                metadata_match: Match[str] | None = re.search(r"\[(.*?)\]",
                                                              line)
                metadata_dict = {}
                if metadata_match:
                    metadata_dict = self._parse_metadata(
                        metadata_match.group(0))
                    line = re.sub(r"\[.*?\]", "", line).strip()

                if line.startswith("start_hub", "end_hub", "hub"):
                    prefix, rest = line.split(":", 1)
                    parts = rest.strip().split()

                    if len(parts) < 3:
                        raise MapParserError(f"Line {line_id}: Invalid zone "
                                             "definition.")
                    name, x, y = parts[0], int(parts[1]), int(parts[2])

                    if prefix == "start_hub" or prefix == "end_hub":
                        metadata_dict["zone"] = "normal"

                    try:
                        zone = ZoneModel(name=name, x=x, y=y, **metadata_dict)
                        self.zones[name] = zone
                    except Exception as e:
                        raise MapParserError(f"Line {line_id}: {str(e)}")

                elif line.startswith("connection:"):
                    _, rest = line.split(":", 1)
                    if '-' not in rest:
                        raise MapParserError(f"Line {line_id}: Invalid"
                                             " connection definition.")

                    zones_parts = rest.strip().split('-')
                    z1, z2 = zones_parts[0].strip(), zones_parts[1].strip()

                    if z1 not in self.zones or z2 not in self.zones:
                        raise MapParserError(f"Line {line_id}: Connection"
                                             " refers to undefined zones.")
                    try:
                        connection = ConnectionModel(zone1=z1, zone2=z2,
                                                     **metadata_dict)
                        self.connections.append(connection)
                    except Exception as e:
                        raise MapParserError(f"Line {line_id}: {str(e)}")
        return self.nb_drone, self.zones, self.connections
