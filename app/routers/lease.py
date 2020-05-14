from fastapi import APIRouter, Response, status
from datetime import datetime
from pony.orm import commit, db_session, RowNotFound

from app.tools import get_user_by_token, create_new_token
from app.models import get_available_cell_types, Lease, get_free_cell

router = APIRouter()


@db_session
@router.post("/new")
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

    l = Lease(start_time=current_time, cell_id=current_cell, user_id=token_user.id, is_returned=False)
    commit()

    current_token = create_new_token(token_user.id, l.id)
    l.token_id = current_token.id
    commit()

    return {"token":current_token.value, "cell": current_cell}
