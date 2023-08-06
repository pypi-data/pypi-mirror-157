"""Utilities to help reduce boilerplate and reuse common functionality, Based to Support Building of Authx & Authx-lite"""

__version__ = "0.0.5"

from authx_core.engine import authxDB
from authx_core.guid import GUID, postgresql
from authx_core.middleware import (
    authxCPU,
    authxMetric,
    authxMiddleware,
    authxRecord,
    authxStats,
)
from authx_core.routers import authxInferring, authxOpenAPI
from authx_core.view import AuthXBasedView

__all__ = [
    "GUID",
    "postgresql",
    "authxDB",
    "authxCPU",
    "authxMetric",
    "authxMiddleware",
    "authxRecord",
    "authxStats",
    "authxOpenAPI",
    "authxInferring",
    "AuthXBasedView",
]
