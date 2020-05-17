from fastapi import APIRouter, Response, status
from datetime import datetime
from pony.orm import commit, db_session, select, RowNotFound, desc

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
            if u.user_id == token_user.id and u.is_returned in (with_closed, False)
        )[:]
    ]

    return {"Leases": l}


@router.post("/take_equipment")
@db_session
def take_equipment(code: str, res: Response):
    if len(code) != 6 or not code.isdigit():
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    t = select(x for x in Token if x.value == code).first()
    if t is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    l = select(x for x in Lease if x.id == t.lease_id).first()
    c = select(x for x in Cell if x.id == l.cell_id).first()

    c.is_empty = True
    c.is_taken = False

    return {f"Cell {c.id} opened!"}


@router.post("/end")
@db_session
def end_lease(token: str, lease_id: int, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error

    try:
        l = Lease[lease_id]
    except RowNotFound:
        l = None

    if l is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": f"No lease with id = {lease_id} exists!"}

    if l.user_id != token_user.id:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": f"Only user with id {l.user_id} can end this lease!"}

    lease_cell = select(x for x in Cell if x.id == l.cell_id).first()
    lease_cell_type = lease_cell.cell_type_id

    c = (
        select(
            c
            for c in Cell
            if c.cell_type_id == lease_cell_type
            and c.is_empty == True
            and c.is_taken == False
        )
        .order_by(lambda x: desc(x.id))
        .first()
    )

    if c is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": f"No empty cells with type {lease_cell_type} exists!"}

    t = select(x for x in Token if x.lease_id == l.id).first()

    c.is_taken = True
    l.cell_id = c.id

    return {"Token": t.value, "Cell": c.id}


@router.post("/return_equipment")
@db_session
def return_equipment(code: str, res: Response):
    if len(code) != 6 or not code.isdigit():
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    t = select(x for x in Token if x.value == code).first()
    if t is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Your code is invalid!"}

    l = select(x for x in Lease if x.id == t.lease_id).first()
    c = select(x for x in Cell if x.id == l.cell_id).first()
    current_time = datetime.utcnow()

    if l.is_returned:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Lease already ended!"}

    c.is_empty = False
    c.is_taken = False
    l.end_time = current_time
    l.is_returned = True

    return {f"Lease {l.id} ended and equipment is returned!"}
