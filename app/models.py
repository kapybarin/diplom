from datetime import datetime
from pony import orm
from os import getenv, environ
from random import randrange

db = orm.Database()


class User(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    email = orm.Optional(str, unique=True, nullable=True)
    first_name = orm.Optional(str, nullable=True)
    token_id = orm.Set('Token')
    last_name = orm.Optional(str, nullable=True)
    leases_id = orm.Set('Lease')
    group_Id = orm.Set('Group')
    pass_id = orm.Set('Pass')
    password = orm.Optional(str)
    is_admin = orm.Optional(bool)


class Cell(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    is_empty = orm.Optional(bool)
    leases_id = orm.Set('Lease')
    cell_type_id = orm.Required('Cell_Type')


class Cell_Type(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Optional(str, nullable=True, unique=True)
    cell_id = orm.Optional(Cell)


class Lease(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    start_time = orm.Required(datetime)
    end_time = orm.Optional(datetime)
    is_returned = orm.Optional(bool)
    cell_id = orm.Required(Cell)
    token_id = orm.Optional('Token')
    user_id = orm.Required(User)


class Group(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    is_admin = orm.Optional(bool)
    user_id = orm.Set(User)
    name = orm.Optional(str)


class Pass(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    user_id = orm.Required(User)
    pass_value = orm.Optional(str, unique=True)


class Token(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    expires_at = orm.Optional(datetime)
    lease_id = orm.Required(Lease)
    user_id = orm.Required(User)
    value = orm.Required(str)


@orm.db_session
def setup_data():
    names = ["Ноутбук", "Документы", "Мышь", "Клавиатура", "Маркеры"]
    try:
        for name in names:
            c = Cell_Type(name=name)
            db.commit()
    except:
        pass


@orm.db_session
def get_available_cell_types():
    types = [t.id for t in orm.select(c for c in Cell_Type)[:]]
    return types


@orm.db_session
def get_free_cell(id: int):
    return randrange(0, 1000)


def setup_database():
    db.bind(provider='postgres', user=getenv("DB_USER"), password=getenv("DB_PASSWORD"), host=getenv("DB_HOST"),
            database=getenv("DB_NAME"))
    db.generate_mapping(create_tables=True)
    setup_data()
    return db
