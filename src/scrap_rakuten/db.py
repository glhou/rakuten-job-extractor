from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from scrap_rakuten.config import Config
from scrap_rakuten.models import Base

_engine = None


def get_engine():
    global _engine
    if _engine:
        return _engine
    _engine = create_engine(Config.db_url.value)
    return _engine


def get_session(engine: Engine | None = None):
    if not engine:
        engine = get_engine()
    with Session(engine) as session:
        yield session


@contextmanager
def session_scope(engine: Engine | None = None) -> Iterator[Session]:
    yield from get_session(engine)


def create_db(engine: Engine | None = None):
    if not engine:
        engine = get_engine()
    Base.metadata.create_all(engine)
