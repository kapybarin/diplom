from fastapi import FastAPI, Response, status
from dotenv import load_dotenv
from pony.orm import db_session

from models import setup_database
from tools import custom_openapi
from models_api import NewUser

load_dotenv()
app = FastAPI()
db = setup_database()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/user/new")
@db_session
def new_user(u: NewUser):
    User(email=u.email, first_name=u.name, last_name=u.surname, password=u.password)


@app.get("/user/{id}")
@db_session
def get_user(id: int, res: Response):
    u = User[id]
    if u is None:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {}
    return u.to_dict()


app.openapi = custom_openapi
