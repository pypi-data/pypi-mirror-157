import pytest
from _pytest.monkeypatch import MonkeyPatch

from authx_core import authxDatabaseSettings
from authx_core.utils import authxClearCaches


@pytest.mark.parametrize(
    "sqlalchemy_database_url", ["sqlite:///./test.db", "sqlite:///./test2.db"]
)
def test_database_settings(
    monkeypatch: MonkeyPatch, sqlalchemy_database_url: str
) -> None:
    monkeypatch.setenv("DB_SQLALCHEMY_URL", sqlalchemy_database_url)

    authxClearCaches()
    assert authxDatabaseSettings().sqlalchemy_url == sqlalchemy_database_url
