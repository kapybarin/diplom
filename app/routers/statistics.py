from fastapi import APIRouter, Response
from pony.orm import db_session, select, count, desc

from app.models import Cell_Type, Cell, Lease, User
from app.models_api import UserGrowth
from app.tools import get_user_by_token

router = APIRouter()


@router.get("/all")
@db_session
def all_statistics(res: Response):
    # token_user, error, code = get_user_by_token(token)
    # if error:
    #    res.status_code = code
    #    return error
    # if not token_user.is_admin:
    #    res.status_code = status.HTTP_400_BAD_REQUEST
    #    return {"err": "Token user is not admin!"}

    user_growth_by_date = [
        UserGrowth(date=x[0], count=x[1])
        for x in select((u.create_date, count(u)) for u in User)[:]
    ]

    all_equipment = [
        x
        for x in select(
            (t.cell_type_id, count(t.id), count(t.is_taken == False)) for t in Cell
        )[:]
    ]

    return {"user_growth_by_date": user_growth_by_date, "tst": all_equipment}
