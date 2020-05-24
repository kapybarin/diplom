from fastapi import APIRouter, Response
from pony.orm import db_session, select, RowNotFound, desc

from app.tools import get_user_by_token
from app.models import Cell_Type, Cell, Lease, User
from app.models_api import CellType

router = APIRouter()


@router.get("/cell_types_available")
@db_session
def get_cell_types(token: str, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error
    types = [CellType(name=t.name, id=t.id) for t in select(c for c in Cell_Type)[:]]
    return types


@router.get("/current_free_types")
@db_session
def current_types(token: str, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error
    cells = [x.to_dict() for x in select(c for c in Cell if c.is_taken == False)[:]]
    free_types = set()
    res = []
    for cell in cells:
        if cell["cell_type_id"] not in free_types:
            free_types.add(cell["cell_type_id"])
            t = dict()
            t["id"] = cell["cell_type_id"]
            try:
                t["name"] = Cell_Type[cell["cell_type_id"]].name
            except RowNotFound:
                t["name"] = None
            res.append(t)

    return res


@router.get("/statuses")
@db_session
def cell_statuses():
    c = [x.to_dict() for x in select(u for u in Cell)[:]]
    types = {str(t.id): t.name for t in select(c for c in Cell_Type)[:]}
    res = []
    for x in c:
        cell = x.copy()
        cell["type_name"] = types[str(cell["cell_type_id"])]
        res.append(cell)

    return {"Cells:": res}


@router.get("/history")
@db_session
def get_cell_history(
    token: str, cell_id: int, res: Response, with_closed: bool = False
):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    l = [
        x.to_dict()
        for x in select(
            t
            for t in Lease
            if t.is_returned in (with_closed, False) and t.cell_id.id == cell_id
        ).order_by(lambda y: desc(y.start_time))[:]
    ]

    history = []
    for lease in l:
        curr = lease.copy()
        try:
            u = User[curr["user_id"]]
            curr["user_name"] = u.first_name
            curr["user_surname"] = u.last_name
            curr["user_email"] = u.email
        except RowNotFound:
            curr["user_name"], curr["user_surname"], curr["user_email"] = (
                None,
                None,
                None,
            )
        history.append(curr)

    return history
