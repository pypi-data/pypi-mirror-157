import inspect
from typing import Any, Callable, List, Type, TypeVar, get_type_hints

from pydantic.typing import is_classvar

T = TypeVar("T")

VIEW_KEY = "__authx_class__"


def _initial_view(cls: Type[Any]) -> None:
    """
     Idempotently modifies the provided `cls`, performing the following modifications:
    * The `__init__` function is updated to set any class-annotated dependencies as instance attributes
    * The `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, VIEW_KEY, False):  # pragma: no cover
        return  # Already initialized
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_params = list(old_signature.parameters.values())[
        1:
    ]  # Skip the first params, which is `self`
    new_params = [
        x
        for x in old_params
        if x.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]
    dependency_names: List[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        params_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_params.append(
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=hint,
                **params_kwargs,
            )
        )
    new_signature = old_signature.replace(parameters=new_params)

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        """Initializer for the class-based view."""
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__signature__", new_signature)
    setattr(cls, "__init__", new_init)
    setattr(cls, VIEW_KEY, True)
