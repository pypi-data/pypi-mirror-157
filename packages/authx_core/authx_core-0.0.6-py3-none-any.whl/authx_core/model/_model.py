from functools import partial

from pydantic import BaseConfig, BaseModel

from authx_core.utils import authxSnake


class _model(BaseModel):
    """
    Intended for use as a base class for externally-facing models.

    Any models that inherit from this class will:
    * accept fields using authxSnake or authxCamel keys
    * use authxCamel keys in the generated OpenAPI spec
    * have orm_mode on by default
        * Because of this, FastAPI will automatically attempt to parse returned orm instances into the model
    """

    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = partial(authxSnake, start_lower=True)


class _message(_model):
    """
    A lightweight utility class intended for use with simple message-returning endpoints.
    """

    detail: str
