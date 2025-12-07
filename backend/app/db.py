from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "job_agent.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Create all tables if they do not exist.
    """
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Provide a session context manager for DB operations.
    """
    with Session(engine) as session:
        yield session
