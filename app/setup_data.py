from app.models import setup_database, Cell_Type


db = setup_database()
names = ["Ноутбук", "Документы", "Мышь", "Клавиатура", "Маркеры"]
for name in names:
    c = Cell_Type(name=name)
    db.commit()