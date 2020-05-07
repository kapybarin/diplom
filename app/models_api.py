from pydantic import BaseModel


class NewUser(BaseModel):
    email: str
    name: str
    surname: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
