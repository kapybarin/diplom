from pydantic import BaseModel


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