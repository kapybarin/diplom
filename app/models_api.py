from pydantic import BaseModel


class NewUser(BaseModel):
    email: str
    name: str
    surname: str
    password: str


class UpdateInfoUser(BaseModel):
    email: str
    name: str
    surname: str
