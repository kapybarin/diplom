from fastapi import APIRouter, Response, status
from pony.orm import db_session, select, commit, RowNotFound

from app.tools import get_user_by_token
from app.models import Pass_Type, Pass
from app.models_api import PassType

router = APIRouter()


@router.post("/add")
@db_session
def add_pass(token: str, pass_value: str, pass_type: int, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    types = [t.id for t in select(c for c in Pass_Type)[:]]
    if pass_type not in types:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "No such pass type exists!"}

    p = Pass(user_id=token_user.id, pass_value=pass_value, pass_type=pass_type)
    commit()
    return p.id


@router.get("/types_available")
@db_session
def get_pass_types(token: str, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error
    types = [PassType(name=t.name, id=t.id) for t in select(c for c in Pass_Type)[:]]
    return types


@router.get("/get_by_user")
@db_session
def get_passes(token: str, res: Response, user_id: int = None):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    if not token_user.is_admin and user_id != token_user.id:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Only admins can view passes of other users!"}

    if user_id is not None:
        check_id = user_id
    else:
        check_id = token_user.id

    types = [PassType(name=t.name, id=t.id) for t in select(c for c in Pass_Type)[:]]
    passes = [x.to_dict() for x in select(t for t in Pass if t.user_id.id == check_id)]
    res = []
    for p in passes:
        curr = p.copy()
        curr["type_name"] = types[curr["pass_type"]]
        res.append(curr)

    return res


@router.get("/all")
@db_session
def get_all_passes(token: str, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    if not token_user.is_admin:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Token user is not admin!"}

    passes = [x.to_dict() for x in select(t for t in Pass)]

    return passes


@router.post("/remove")
@db_session
def remove_pass(token: str, pass_id: int, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    try:
        p = Pass[pass_id]
    except RowNotFound:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "No such pass exists!"}

    if p.user_id.id != token_user.id:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "You can only remove your own passes!"}

    p.delete()
    commit()
    return {"Success"}
