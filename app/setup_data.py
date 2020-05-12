from pony.orm import commit, db_session

from app.models import setup_database, Cell_Type


@db_session
def prepare_data(database):
    Cell_Type(name="Ноутбук")
    Cell_Type(name="Документы")
    Cell_Type(name="Мышь")
    Cell_Type(name="Клавиатура")
    Cell_Type(name="Маркеры")

    commit()


db = setup_database()
prepare_data(db)
