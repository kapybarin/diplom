from fastapi import APIRouter, Response
from pony.orm import db_session, select

from app.tools import get_user_by_token
from app.models import Cell_Type

router = APIRouter()


@router.get("/cell_types_available")
@db_session
def get_cell_types(token: str, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error
    type = [t.to_dict() for t in select(c for c in Cell_Type)[:]]
    return {"available":type}
