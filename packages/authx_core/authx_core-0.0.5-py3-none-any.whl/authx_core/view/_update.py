import inspect
from typing import Any, List, Type, TypeVar, Union

from fastapi import Depends
from starlette.routing import Route, WebSocketRoute

T = TypeVar("T")


def _update_view_signature(cls: Type[Any], route: Union[Route, WebSocketRoute]) -> None:
    """Updates the signature of the provided route's endpoint to match the signature of the class-based view."""
    old_endpoint = route.endpoint
    old_signature = inspect.signature(old_endpoint)
    old_params: List[inspect.Parameter] = list(old_signature.parameters.values())
    old_first_params = old_params[0]
    new_first_params = old_first_params.replace(default=Depends(cls))
    new_parameters = [new_first_params] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
        for parameter in old_params[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, "__signature__", new_signature)
