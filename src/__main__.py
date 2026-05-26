from src.models import ZoneModel, ConnectionModel
from src.parser import ConfigParser, MapParserError
from src.simulation import Simulation
from typing import Dict, List


def main() -> None:
    choice: int = int(input("What level you to do (0: easy, 1: "
                            "medium, 2: hard, 3: challenge) -> "))
    files: List[str] = [
        "maps/easy/01_linear_path.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/hard/01_maze_nightmare.txt",
        "maps/challenger/01_the_impossible_dream.txt"
        ]
    file_path: str = files[choice]
    try:
        map_config: ConfigParser = ConfigParser(file_path=file_path)
    except Exception as e:
        print(e)
        return
    simu: Simulation = Simulation(map=map_config)
    simu.resolve_all_paths

    from src.visualizer import Visualizer
    visu: Visualizer = Visualizer(simu=simu)
    visu.run()


if __name__ == "__main__":
    main()
    print("\nFINISH")
