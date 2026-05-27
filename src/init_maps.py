from pathlib import Path
from typing import List, Tuple

def init_maps() -> List[Tuple[str, str]]:
    maps_list = []
    
    for p in Path("maps/").rglob('*'):
        if p.is_file():
            map_name = p.name 
            difficulty = p.parent.name if p.parent.name != "maps" else ""
            if difficulty:
                maps_list.append(("maps/" + difficulty + '/' + map_name, difficulty.capitalize()))
    return maps_list