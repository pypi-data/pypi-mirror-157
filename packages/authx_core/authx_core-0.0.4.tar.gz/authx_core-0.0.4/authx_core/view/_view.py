import inspect
from typing import Callable, Type, TypeVar

from fastapi import APIRouter
from starlette.routing import Route, WebSocketRoute

T = TypeVar("T")

from authx_core.view._initial import _initial_view as authxInitialView
from authx_core.view._update import _update_view_signature as authxUpdateViewSignature


def AuthXBasedView(router: APIRouter) -> Callable[[Type[T]], Type[T]]:
    """
    This function returns a decorator that converts the decorated into a class-based view for the provided router.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        return _authx_based_view(router, cls)

    return decorator


def _authx_based_view(router: APIRouter, cls: Type[T]) -> Type[T]:
    """
    Replaces any methods of the provided class `cls` that are endpoints of routes in `router` with updated
    function calls that will properly inject an instance of `cls`.
    """
    authxInitialView(cls)
    cbv_router = APIRouter()
    function_members = inspect.getmembers(cls, inspect.isfunction)
    functions_set = {func for _, func in function_members}
    cbv_routes = [
        route
        for route in router.routes
        if isinstance(route, (Route, WebSocketRoute))
        and route.endpoint in functions_set
    ]
    for route in cbv_routes:
        router.routes.remove(route)
        authxUpdateViewSignature(cls, route)
        cbv_router.routes.append(route)
    router.include_router(cbv_router)
    return cls
