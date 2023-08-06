from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import validator

from authx_core.settings._backend import authxBackend
from authx_core.settings._base import _base as authxBaseSettings


class authxDatabase(authxBaseSettings):
    """Settings for the database."""

    backend: authxBackend = None  # type: ignore

    user: Optional[str]
    password: Optional[str]
    host: Optional[str]
    db: Optional[str]

    sqlalchemy_url: str = None  # type: ignore

    log_sqlalchemy_sql_statements: bool = False

    min_size: int = 10
    max_size: int = 10
    force_rollback: bool = False

    @validator("sqlalchemy_url", pre=True, always=True)
    def _sqlalchemy_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v is None:
            backend = values.get("backend")
            backend = backend.value if backend is not None else None

            user = values["user"]
            password = values["password"]
            host = values["host"]
            db = values["db"]

            v = f"{backend}://{user}:{password}@{host}/{db}"
        return v

    class Config:
        env_prefix = "db_"


@lru_cache()
def get_database_settings() -> authxDatabase:
    """Get the database settings."""
    return authxDatabase()
