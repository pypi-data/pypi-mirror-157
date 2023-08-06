from fastapi import FastAPI
from starlette.routing import Match, Mount
from starlette.types import Scope


class _metric:
    """
    This class generates the route "name" used when logging timing records.

    If the route has `endpoint` and `name` attributes, the endpoint's module and route's name will be used
    (along with an optional prefix that can be used, e.g., to distinguish between multiple mounted ASGI apps).

    By default, in FastAPI the route name is the `__name__` of the route's function (or type if it is a callable class
    instance).
    """

    def __init__(self, prefix: str, app: FastAPI):
        if prefix:
            prefix += "."
        self.prefix = prefix
        self.app = app

    def __call__(self, scope: Scope) -> str:
        """
        Generates the actual name to use when logging timing metrics for a specified ASGI Scope
        """
        route = next(
            (r for r in self.app.router.routes if r.matches(scope)[0] == Match.FULL),
            None,
        )

        if hasattr(route, "endpoint") and hasattr(route, "name"):
            return f"{self.prefix}{route.endpoint.__module__}.{route.name}"  # type: ignore
        elif isinstance(route, Mount):
            return f"{type(route.app).__name__}<{route.name!r}>"
        else:
            return str(f"<Path: {scope['path']}>")
