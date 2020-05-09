from fastapi import APIRouter, status, Response
from pony.orm import db_session, commit, RowNotFound, select

from app.models import User
from app.models_api import NewUser, UpdateInfoUser
from app.tools import is_valid_email, get_password_hash, verify_password, create_access_token, validate_token

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
def get_user(id: int, token: str, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}
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


@router.post("/make_admin")
@db_session
def user_admin(id: int, token: str, is_admin: bool, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}
    try:
        u = User[id]
    except RowNotFound:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f'No user with id {id} found'}
    u.is_admin = is_admin
    commit()
    return {"id": u.id, "is_admin": u.is_admin}


@router.get("/all")
@db_session
def list_users(token: str, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}
    curr_user = User.get(email=email)
    if not curr_user.is_admin:
        res.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        return {"err": f'User with email {email} is not admin!'}
    u = [x.to_dict() for x in select(u for u in User)[:]]

    return {"Users": u}


@router.get("/update_info")
@db_session
def update_user_info(user: UpdateInfoUser, token: str, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}
    token_user = User.get(email=email)
    if token_user.email != user.email and not token_user.is_admin:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Non admin users can only update their info!"}

    user_for_update = User.get(email=user)
    if user_for_update is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": f'No user with email {user.email} found!'}

    user_for_update.email = user.email
    user_for_update.first_name = user.name
    user_for_update.last_name = user.surname
    commit()

    res = user_for_update.to_dict()
    res.pop("password", None)
    return res


@router.get("/update_password")
@db_session
def update_password(token: str, old_password: str, new_password: str, res: Response):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"err": "Token is not valid"}

    token_user = User.get(email=email)
    is_valid_pass = verify_password(old_password, token_user.password)
    if not is_valid_pass:
        res.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": f'Incorrect old password'}

    hashed_new_pass = get_password_hash(new_password)
    token_user.password = hashed_new_pass

    return {"Success!"}
