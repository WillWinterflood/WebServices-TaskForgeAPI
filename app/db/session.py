from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def ensure_sqlite_directory_exists(database_url):
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite":
        return {}

    database = url.database
    if not database or database == ":memory:":
        return {"check_same_thread": False}

    Path(database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    return {"check_same_thread": False}


connect_args = ensure_sqlite_directory_exists(settings.database_url)
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
