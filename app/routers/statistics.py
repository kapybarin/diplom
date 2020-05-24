from fastapi import APIRouter, Response
from pony.orm import db_session, select, count, desc

from app.models import Cell_Type, Cell, Lease, User
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

    rows = [
        x.to_dict()
        for x in select((u.create_date, count(u)) for u in User).order_by(
            lambda x: desc(x.create_date)
        )[:]
    ]
    user_growth_by_date = dict()
    if rows is not None:
        for row in rows:
            user_growth_by_date[row["create_date"]] = row["count"]

    return {"user_growth_by_date": user_growth_by_date}
