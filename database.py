from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./microblog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    db = SessionLocal()
    from models import User
    try:
        # проверим наличие тестового пользователя
        # user = db.query(User).filter(User.api_key == "test").first()
        if not db.query(User).first():
            users = [
                User(name="ilmi", api_key="test", display_name="Ilmi",
                     avatar_url="https://i.pravatar.cc/150?u=ilmi"),
                User(name="petya", api_key="petya123", display_name="Petya",
                     avatar_url="https://i.pravatar.cc/150?u=petya"),
                User(name="masha", api_key="masha456", display_name="Masha",
                     avatar_url="https://i.pravatar.cc/150?u=masha"),
            ]
            db.add_all(users)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()