"""Utilities to help reduce boilerplate and reuse common functionality, Based to Support Building of Authx & Authx-lite"""

__version__ = "0.0.3"

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
]
