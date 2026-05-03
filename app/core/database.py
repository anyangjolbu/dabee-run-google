from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.core.config import get_settings
import os

settings = get_settings()

# Ensure data directory exists if using sqlite
if settings.database_url.startswith("sqlite"):
    os.makedirs(os.path.dirname(settings.database_url.replace("sqlite:///", "")), exist_ok=True)

# WAL mode is recommended for SQLite in ARCHITECTURE.md
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url, connect_args=connect_args
)

if settings.database_url.startswith("sqlite"):
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
