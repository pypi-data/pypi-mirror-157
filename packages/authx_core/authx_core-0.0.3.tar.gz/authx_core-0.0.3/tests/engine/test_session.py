import uuid
from pathlib import Path
from typing import Iterator

import pytest
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from starlette.testclient import TestClient

from tests.conftest import session_maker as Session

other_db_path = Path("./test2.db")
other_db_uri = f"sqlite:///{other_db_path}?check_same_thread=False"


@pytest.fixture()
def use_uninitialized_db() -> Iterator[None]:
    if other_db_path.exists():
        other_db_path.unlink()
    original_uri = Session.database_url
    Session.database_url = other_db_uri
    Session.reset_cache()
    yield
    Session.database_url = original_uri
    Session.reset_cache()
    if other_db_path.exists():
        other_db_path.unlink()


def test_fail(test_app: FastAPI, use_uninitialized_db: None) -> None:
    test_client = TestClient(test_app)
    Session.reset_cache()
    Session.database_url = other_db_uri
    random_id = uuid.uuid4()
    with pytest.raises(OperationalError) as exc_info:
        test_client.get(f"/{random_id}")
    assert "no such table: user" in str(exc_info.value)
