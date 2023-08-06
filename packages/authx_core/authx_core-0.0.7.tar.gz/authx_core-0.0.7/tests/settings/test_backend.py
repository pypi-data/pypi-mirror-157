import pytest
from _pytest.monkeypatch import MonkeyPatch

from authx_core import authxBackend
from authx_core.engine import authx_engine
from authx_core.utils import authxClearCaches


@pytest.mark.parametrize(
    "sqlalchemy_database_url,expected_backend",
    [
        ("sqlite://", authxBackend.sqlite),
        ("postgresql://a:b@c/d", authxBackend.postgresql),
    ],
)
def test_database_backend(
    monkeypatch: MonkeyPatch,
    sqlalchemy_database_url: str,
    expected_backend: authxBackend,
) -> None:
    monkeypatch.setenv("DB_SQLALCHEMY_URL", sqlalchemy_database_url)
    authxClearCaches()
    engine = authx_engine(url=sqlalchemy_database_url)
    assert authxBackend._from_engine(engine) == expected_backend
