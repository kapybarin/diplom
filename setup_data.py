from app.models import setup_database, Cell_Type
from dotenv import load_dotenv


def main():
    load_dotenv()
    db = setup_database()
    db.generate_mapping(create_tables=True)
    names = ["Ноутбук", "Документы", "Мышь", "Клавиатура", "Маркеры"]
    for name in names:
        c = Cell_Type(name=name)
        db.commit()


if __name__ == "__main__":
    main()