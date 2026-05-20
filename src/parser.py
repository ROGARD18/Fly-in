import re
from typing import List, Tuple, Any, Dict
from src.models import ZoneModel, ConnectionModel


class MapParser:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.nb_drone: int = 0
        self.zones: Dict[str, ZoneModel] = {}
        self.connections: List[ConnectionModel] = []

    def _parse_metadata(self, metadata: str) -> Dict[str, Any] | None:
        metadata: Dict[str, Any] = {}
        if not metadata:
            return None

        metadata: str = metadata.strip("[]")
        pairs = re.findall(r'(\w+)(?:[=\s](\w+))?', metadata)
        for key, value in pairs:
            if not value:
                continue
            if value.isdigit():
                metadata[key] = int(value)
            else:
                metadata[key] = value
        return metadata

    def parse(self) -> Tuple[int, Dict[str, ZoneModel], List[ConnectionModel]]:
        with open(self.file_path, 'r') as f:
            for line_idx, line in enumerate(f, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                   continue

                metadata 