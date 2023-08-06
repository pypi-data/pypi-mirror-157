import pytest
from _pytest.monkeypatch import MonkeyPatch

from authx_core import authxDatabaseSettings
from authx_core.utils import authxClearCaches


def test_postgres_sqlalchemy_url(monkeypatch: MonkeyPatch) -> None:
    environment = {
        "DB_BACKEND": "postgresql",
        "DB_USER": "a",
        "DB_PASSWORD": "b",
        "DB_HOST": "c",
        "db_db": "d",
    }
    for k, v in environment.items():
        monkeypatch.setenv(k, v)

    authxClearCaches()
    assert authxDatabaseSettings().sqlalchemy_url == "postgresql://a:b@c/d"
