from typing import Callable, Optional

from fastapi import FastAPI
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from authx_core.middleware._metric import _metric as authxMetric
from authx_core.middleware._stats import _stats as authxStats

TIMER_ATTRIBUTE = "__authx_timer__"


def _timing_middleware(
    app: FastAPI,
    record: Optional[Callable[[str], None]] = None,
    prefix: str = "",
    exclude: Optional[str] = None,
) -> None:
    """
    Adds a middleware to the provided `app` that records timing metrics using the provided `record` callable.

    Typically `record` would be something like `logger.info` for a `logging.Logger` instance.

    The provided `prefix` is used when generating route names.
    """
    metric_namer = authxMetric(prefix=prefix, app=app)

    @app.middleware("http")
    async def timing_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        metric_name = metric_namer(request.scope)
        with authxStats(metric_name, record=record, exclude=exclude) as timer:
            setattr(request.state, TIMER_ATTRIBUTE, timer)
            response = await call_next(request)
        return response
