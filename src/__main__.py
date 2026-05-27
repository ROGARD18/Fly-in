from src.models import ZoneModel, ConnectionModel
from src.parser import ConfigParser, MapParserError
from src.simulation import Simulation
from typing import Dict, List
from src.init_maps import init_maps
from src.visualizer import Visualizer


def main() -> None:
    all_maps: List[str] = init_maps()
    # try:  
    choice: str = Visualizer.run_menu(all_maps)
    # except Exception as e:
    #     print(f"Error !: {e}")
    try:
        map_config: ConfigParser = ConfigParser(file_path=choice)
    except Exception as e:
        print(e)
        return
    simu: Simulation = Simulation(map=map_config)
    simu.resolve_all_paths

    visu: Visualizer = Visualizer(simu=simu)
    visu.run()


if __name__ == "__main__":
    main()
    print("\nFINISH")
