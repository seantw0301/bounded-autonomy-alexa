import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = os.environ.get("BA_DB", str(ROOT / "data" / "app.db"))
PRODUCTS_PATH = os.environ.get("BA_PRODUCTS", str(ROOT / "data" / "products.json"))

engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False, "timeout": 15}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


def init_db():
    from db import models  # noqa: F401

    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
