from fastapi import APIRouter, Response
from pony.orm import db_session, select, RowNotFound, desc

from app.models import Cell_Type, Cell, Lease, User
from app.tools import get_user_by_token

router = APIRouter()


@router.get("/all")
@db_session
async def all_statistics(res: Response):
    # token_user, error, code = get_user_by_token(token)
    # if error:
    #    res.status_code = code
    #    return error

    # fmt: off
    rows = select(
        '''select u.create_date as date, count(u.id) as count
           from "user" u
           group by u.create_date
           order by u.create_date'''
    )
    # fmt: on
    user_growth_by_date = dict()
    if rows is not None:
        for row in rows:
            user_growth_by_date[row[0]] = row[1]

    return {"user_growth_by_date": user_growth_by_date}
