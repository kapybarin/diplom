from fastapi import APIRouter, Response
from pony.orm import db_session, select, RowNotFound

from app.tools import get_user_by_token
from app.models import Cell_Type, Cell
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
