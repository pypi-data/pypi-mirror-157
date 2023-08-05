from pathlib import Path
from typing import Iterator
from uuid import UUID

import pytest
import sqlalchemy as sa
from fastapi import Depends, FastAPI
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from authx_core import GUID, authxDB
from authx_core.engine import authx_engine
from authx_core.guid.type import GUID_DEFAULT_SQLITE

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = sa.Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = sa.Column(sa.String, nullable=False)
    related_id = sa.Column(GUID)


test_db_path = Path("./test.db")
database_url = f"sqlite:///{test_db_path}?check_same_thread=False"
session_maker = authxDB(database_url=database_url)


def get_db() -> Iterator[Session]:
    yield from session_maker.get_db()


app = FastAPI()


@app.get("/{user_id}")
def get_user_name(db: Session = Depends(get_db), *, user_id: UUID) -> str:
    user = db.query(User).get(user_id)
    return user.name  # type: ignore


@pytest.fixture(scope="module")
def test_app() -> Iterator[FastAPI]:
    if test_db_path.exists():
        test_db_path.unlink()

    engine = authx_engine(database_url)
    Base.metadata.create_all(bind=engine)

    yield app
    if test_db_path.exists():
        test_db_path.unlink()
