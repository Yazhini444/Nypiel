"""Shared SQLAlchemy database configuration for FastAPI and Streamlit.

SQLite is the zero-config default. Set DATABASE_URL to use another database
or to place SQLite on a persistent mounted volume in deployment.

Streamlit Community Cloud persistence note:
The local SQLite filesystem on Streamlit Community Cloud is ephemeral across
app/container recreations and restarts. Local SQLite storage provides session
and container lifecycle persistence during local development and active
containers, but is not guaranteed permanent account storage across container
rebuilds or redeployments. For permanent multi-instance cloud persistence,
configure DATABASE_URL to point to a managed database (e.g., PostgreSQL).
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

ROOT_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(ROOT_DIR / 'nypiel.db').as_posix()}",
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
