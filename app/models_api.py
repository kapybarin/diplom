from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NewUser(BaseModel):
    email: str
    name: str
    surname: str
    password: str


class UpdateInfoUser(BaseModel):
    id: int
    name: str
    surname: str


class CellType(BaseModel):
    id: int
    name: str


class UserGrowth(BaseModel):
    date: Optional[datetime] = None
    count: int


class EquipmentFreeRatio(BaseModel):
    id: int
    free: int
    total: int
    name: str = ""


class LeasesByType(BaseModel):
    type_id: int
    count: int
    name: str = ""


class LeasesByTypeAndDate(BaseModel):
    type_id: int
    count: int
    name: str = ""
    date: str = None
