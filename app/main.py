from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from pony.orm import db_session, RowNotFound, commit
from jwt import PyJWTError
import jwt

from models import setup_database, User
from models_api import NewUser, TokenData
from tools import is_valid_email, verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM

load_dotenv()
app = FastAPI()
db = setup_database()

origins = [
    "http://api.noirdjinn.dev",
    "https://api.noirdjinn.dev",
    "http://localhost",
    "http://localhost:3000",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TakeAndGo",
        version="0.0.1",
        description="Smart bookshelf project",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/Svintsova/TakeAndGo/master/public/logo192.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@db_session
def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return False, None
    except PyJWTError:
        return False, None
    user = User.find(email=email)
    if user is None:
        return False, None
    return True, email


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/user/new")
@db_session
def new_user(u: NewUser, res: Response):
    email_valid, txt = is_valid_email(u.email)
    if email_valid is False:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": txt}
    curr_user = User.get(email=txt)
    if curr_user is None:
        hashed_pass = get_password_hash(u.password)
        User(email=txt, first_name=u.name, last_name=u.surname, password=hashed_pass)
        commit()
        return {"id": User.get(email=txt).id}
    else:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f'User already exists with the same email and id {curr_user.id}'}


@app.get("/user/{id}")
@db_session
def get_user(id: int, res: Response):
    try:
        u = User[id]
    except RowNotFound:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f'No user with id {id} found'}
    message = u.to_dict()
    message.pop("password", None)
    return message


@app.post("/user/authenticate")
@db_session
def user_auth(email: str, password: str, res: Response):
    curr_user = User.get(email=email)
    if curr_user is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f'No user with email - {email} found'}
    is_valid_pass = verify_password(password, curr_user.password)
    if not is_valid_pass:
        res.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": f'Incorrect password'}
    access_token = create_access_token(
        data={"sub": curr_user.email}
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": curr_user.id}


@app.get("/user/all")
@db_session
def list_users(token: str, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}
    u = [x.to_dict() for x in User[:]]

    return {"Users": u}


app.openapi = custom_openapi
