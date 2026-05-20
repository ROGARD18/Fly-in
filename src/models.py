from typing import List, Literal, Optional
from pydantic import BaseModel, Field

ZoneType = Literal["normal", "blocked", "restricted", "priority"]


class ZoneModel(BaseModel):

    model_config = {
        "popultate_by_name": True
    }
    name: str = Field(frozen=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    zone_type: ZoneType = Field(default="normal", frozen=True)
    color: Optional[str] = Field(default=None, frozen=True)
    max_capacity: int = Field(default=1, ge=1, frozen=True)

    neighbors: List[str] = Field(default_factory=list)


class ConnectionModel(BaseModel):

    model_config = {
        "frozen": True
    }
    zone1: str
    zone2: str
    distance: float = Field(default=1.0, ge=0)
