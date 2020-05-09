from fastapi import APIRouter, status, Response
from pony.orm import db_session, commit, RowNotFound, select

from ..models import User
from ..models_api import NewUser
from ..tools import is_valid_email, get_password_hash, verify_password, create_access_token, validate_token

router = APIRouter()


@router.post("/new")
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


@router.get("/id/{id}")
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


@router.post("/authenticate")
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
    return {"access_token": access_token, "user_id": curr_user.id}


@router.get("/")
@db_session
def list_users(token: str, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}
    u = [x.to_dict() for x in select(u for u in User)[:]]

    return {"Users": u}
