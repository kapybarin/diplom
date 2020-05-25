from fastapi import APIRouter, Response, status
from pony.orm import db_session, select, count, desc

from app.models import Cell_Type, Cell, User, db
from app.models_api import (
    UserGrowth,
    EquipmentFreeRatio,
    CellType,
    LeasesByType,
    LeasesByTypeAndDate,
)
from app.tools import get_user_by_token

router = APIRouter()


@router.get("/all")
@db_session
def all_statistics(token: str, res: Response):
    token_user, error, code = get_user_by_token(token)
    if error:
        res.status_code = code
        return error
    if not token_user.is_admin:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"err": "Token user is not admin!"}

    user_growth_by_date = [
        UserGrowth(date=x[0], count=x[1])
        for x in select((u.create_date, count(u)) for u in User)[:]
    ]

    cell_types = [
        CellType(name=t.name, id=t.id)
        for t in (select(c for c in Cell_Type).order_by(lambda x: desc(x.id)))[:]
    ]

    equipment_free_ratio = [
        EquipmentFreeRatio(id=x[0], free=x[2], total=x[1], name=cell_types[-x[0]].name)
        for x in select(
            (t.cell_type_id, count(t.id), count(t.is_taken == False)) for t in Cell
        )[:]
    ]

    leases_by_type = [
        LeasesByType(type_id=x[0], name=x[1], count=x[2])
        for x in db.select(
            """select c.cell_type_id as id, min(ct.name) as name, count(l.id)
               from lease l
               join cell c on c.id = l.cell_id
               join cell_type ct on c.cell_type_id = ct.id
               group by c.cell_type_id
               order by c.cell_type_id"""
        )
    ]

    leases_by_type_and_date = [
        LeasesByTypeAndDate(type_id=x[0], name=x[1], count=x[2], date=x[3])
        for x in db.select(
            """select c.cell_type_id as id, min(ct.name) as name, count(l.id) as count, date(date_trunc('day', l.start_time)) as day
               from lease l
               join cell c on c.id = l.cell_id
               join cell_type ct on c.cell_type_id = ct.id
               group by c.cell_type_id, date_trunc('day', l.start_time)
               order by date_trunc('day', l.start_time), c.cell_type_id"""
        )
    ]

    return {
        "user_growth_by_date": user_growth_by_date,
        "equipment_free_ratio": equipment_free_ratio,
        "leases_by_type": leases_by_type,
        "leases_by_type_and_date": leases_by_type_and_date,
    }
