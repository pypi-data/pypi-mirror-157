"""The `authx_core.engine.authxDB` class conveniently wraps session-making functionality for use with
FastAPI. """

from authx_core.engine.session import SessionMaker as authxDB
from authx_core.engine.session import _engine as authx_engine
from authx_core.engine.session import _get_db as authx_get_db
from authx_core.engine.session import _sessionmaker_for_engine as authx_sessionmaker
from authx_core.engine.session import context_session as authx_context_session

__all__ = [
    "authxDB",
    "authx_engine",
    "authx_sessionmaker",
    "authx_context_session",
    "authx_get_db",
]
