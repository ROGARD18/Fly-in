from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel, Field

ZoneType = Literal["normal", "blocked", "restricted", "priority"]
StepType = Tuple[str, int]


class ZoneModel(BaseModel):

    model_config = {
        "popultate_by_name": True
    }
    name: str = Field(frozen=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    zone_type: ZoneType = Field(default="normal", alias="zone", frozen=True)
    color: Optional[str] = Field(default=None, frozen=True)
    max_capacity: int = Field(default=1, ge=1, frozen=True)
    distance: int = Field(default=0, ge=0)

    neighbors: List[str] = Field(default_factory=list)


class ConnectionModel(BaseModel):

    model_config = {
        "frozen": True
    }
    zone1: str
    zone2: str
    distance: float = Field(default=1.0, ge=0)


class DroneModel():
    def __init__(self, id: int):
        self.id: int = id
        self.path: str = List[StepType]
