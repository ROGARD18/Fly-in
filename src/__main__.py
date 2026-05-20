from src.models import ZoneModel, ConnectionModel
from src.parser import ConfigParser, MapParserError
from src.simulation import Simulation
from typing import Dict, List


def main() -> None:
    choice: int = int(input("What level you to do (1: easy, 2: "
                            "medium, 3: hard) -> "))
    files: List[str] = [
        "maps/easy/01_linear_path.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/hard/01_maze_nightmare.txt"
        ]
    file_path: str = files[choice]
    try:
        map_config: ConfigParser = ConfigParser(file_path=file_path)
    except Exception as e:
        print(e)
        return
    # print(type(map_config))
    simu: Simulation = Simulation(map=map_config)
    simu.determine_distance_to_goal()
    print()
    for zone in simu.map.zones:
        print(type(simu.map.zones.get("zone")))
        print(f"{zone} is {zone} from goal")


if __name__ == "__main__":
    main()
    print("\nFINISH")
