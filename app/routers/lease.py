from fastapi import APIRouter, Response, status
from datetime import datetime
from pony.orm import commit, db_session, select, RowNotFound

from app.tools import get_user_by_token, create_new_token
from app.models import get_available_cell_types, Lease, get_free_cell, Token, Cell

router = APIRouter()


@router.post("/new")
@db_session
def new_lease(token: str, cell_type: int, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    available_cell_types = get_available_cell_types()
    if cell_type not in available_cell_types:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "No cell with such type is available!"}

    current_time = datetime.utcnow()
    current_cell = get_free_cell(cell_type)
    if current_cell is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "All equipment with such type is taken!"}

    l = Lease(
        start_time=current_time,
        cell_id=current_cell.id,
        user_id=token_user.id,
        is_returned=False,
    )
    commit()

    current_token = create_new_token(token_user.id, l.id)
    l.token_id = current_token.id
    current_cell.is_taken = True
    commit()

    return {"token": current_token.value, "cell": current_cell.id}


@router.get("/leases_by_user")
@db_session
def get_leases_by_user(token: str, res: Response, with_closed: bool = False):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    l = [
        x.to_dict()
        for x in select(
            u
            for u in Lease
            if u.user_id.id == token_user.id and u.is_returned in (with_closed, False)
        )[:]
    ]

    res = []
    for lease in l:
        t = Token.get(lease_id=lease["id"])
        if t is None:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"err": f"Lease without token with id {lease['id']}"}
        try:
            c = Cell[lease["cell_id"]]
        except RowNotFound:
            c = None
        if c is None:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"err": f"Lease without cell with id {lease['id']}"}
        current = lease
        current["token"] = t.value
        current["cell_type"] = c.cell_type_id
        res.append(current)

    return res


@router.post("/take_equipment")
@db_session
def take_equipment(code: str, res: Response):
    if len(code) != 4 or not code.isdigit():
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    t = select(x for x in Token if x.value == code).first()
    if t is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    l = select(x for x in Lease if x.id == t.lease_id.id).first()
    c = select(x for x in Cell if x.id == l.cell_id.id).first()

    if l.is_returned:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Lease already ended!"}

    if c.is_empty:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Already taken!"}

    c.is_empty = True

    return {f"Cell {c.id} opened!"}


@router.post("/return_equipment")
@db_session
def return_equipment(code: str, res: Response):
    if len(code) != 4 or not code.isdigit():
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    t = select(x for x in Token if x.value == code).first()
    if t is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    l = select(x for x in Lease if x.id == t.lease_id.id).first()
    c = select(x for x in Cell if x.id == l.cell_id.id).first()
    current_time = datetime.utcnow()

    if l.is_returned:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Lease already ended!"}

    if c.is_empty == False:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Cell is not empty!"}

    c.is_empty = False
    c.is_taken = False
    l.end_time = current_time
    l.is_returned = True

    return {f"Lease {l.id} ended and equipment is returned!"}


@router.get("/all")
@db_session
def get_all_leases(token: str, res: Response, with_closed: bool = False):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    if not token_user.is_admin:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Token user is not admin!"}

    l = [
        x.to_dict()
        for x in select(t for t in Lease if t.is_returned in (with_closed, False))[:]
    ]

    return l


@router.post("/cancel")
@db_session
def cancel_lease(token: str, lease_id: int, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    try:
        l = Lease[lease_id]
    except RowNotFound:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "No such lease exists!"}

    l.delete()
    return {f"Lease with {lease_id} id deleted!"}
