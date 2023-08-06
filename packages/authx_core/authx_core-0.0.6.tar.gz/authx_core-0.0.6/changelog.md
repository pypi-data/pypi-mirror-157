# Changelog

## 0.0.5

### Camel Case

The `authx_core.utils.authxCamel` or `authx_core.utils.authxSnake` module
contains functions for converting `camelCase` or `CamelCase` strings to
`snake_case`, and vice versa:

```python
from authx_core.utils import  authxSnake, authxCamel

assert authxSnake("some_field_name", start_lower=False) == "SomeFieldName"
assert authxSnake("some_field_name", start_lower=True) == "someFieldName"
assert authxCamel("someFieldName") == "some_field_name"
assert authxCamel("SomeFieldName") == "some_field_name"
```

These functions are used to ensure `snake_case` can be used in your python code,
and `camelCase` attributes in external `JSON`.

But they can also come in handy in other places -- for example, you could use
them to ensure tables declared using SQLAlchemy's declarative API are named
using `snake_case`:

```python
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from authx_core.utils import  authxCamel


class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        return authxCamel(cls.__name__)


Base = declarative_base(cls=CustomBase)
```

If you were to create a `class MyUser(Base):` using `Base` defined above, the
resulting database table would be named `my_user`.

### Enums

Using enums as fields of a JSON payloads is a great way to force provided values
into one of a limited number of self-documenting fields.

However, integer-valued enums can make it more difficult to inspect payloads and
debug endpoint calls, especially if the client and server are using different
code bases.

For most applications, the development benefits of using string-valued enums
vastly outweigh the minimal performance/bandwidth tradeoffs.

Creating a string-valued enum for use with pydantic/FastAPI that is properly
encoded in the OpenAPI spec is as easy as inheriting from `str` in addition to
`enum.Enum`:

```python
from enum import Enum

class MyEnum(str, Enum):
    value_a = "value_a"
    value_b = "value_b"
```

With this approach is that if you rename one of the enum values (for example,
using an IDE), you can end up with the name and value differing, which may lead
to confusing errors.

For example, if you refactored the above as follows (forgetting to change the
associated values), you'll get pydantic parsing errors if you use the new
_names_ instead of the values in JSON bodies:

```python
from enum import Enum

class MyEnum(str, Enum):
    choice_a = "value_a"
    choice_b = "value_b"
```

The standard library's `enum` package provides a way to automatically generate
values: [`auto`](https://docs.python.org/3/library/enum.html#enum.auto).

By default, `auto` will generate integer values, but this behavior can be
overridden and the official python docs include a detailed section about
[how to do this](https://docs.python.org/3/library/enum.html#using-automatic-values).

Rather than repeating this definition in each new project, to reduce boilerplate
you can just inherit from `authx_core.utils.authxStrEnum` directly to get this
behavior:

```python
from enum import auto

from authx_core.utils import authxStrEnum


class MyEnum(authxStrEnum):
    choice_a = auto()
    choice_b = auto()


assert MyEnum.choice_a.name == MyEnum.choice_a.value == "choice_a"
assert MyEnum.choice_b.name == MyEnum.choice_b.value == "choice_b"
```

You can also use `authx_core.utils.authxCamelStrEnum` to get camelCase values:

```python
from enum import auto

from authx_core.utils import authxCamelStrEnum


class MyEnum(authxCamelStrEnum):
    choice_one = auto()
    choice_two = auto()


assert MyEnum.choice_a.name == MyEnum.choice_a.value == "choiceOne"
assert MyEnum.choice_b.name == MyEnum.choice_b.value == "choiceTwo"
```

## 0.0.4

Using the `authx_core.AuthXBasedView` decorator, we can consolidate the endpoint
signatures and reduce the number of repeated dependencies.

To use the `@AuthXBasedView` decorator, you need to:

- Create an APIRouter to which you will add the endpoints
- Create a class whose methods will be endpoints with shared dependencies, and
  decorate it with `@AuthXBasedView(router)`
- For each shared dependency, add a class attribute with a value of type
  `Depends`
- Replace the use of the original "unshared" dependencies with accesses like
  `self.dependency`

## 0.0.3

### OpenAPI

To simplify your operation IDs, you can use `authx_core.authxOpenAPI` to replace
the generated operation IDs with ones generated using _only_ the function name:

```python
from fastapi import FastAPI

from authx_core import authxOpenAPI

app = FastAPI()


@app.get("/api/v1/resource/{resource_id}")
def get_resource(resource_id: int) -> int:
    return resource_id


authxOpenAPI(app)

path_spec = app.openapi()["paths"]["/api/v1/resource/{resource_id}"]
operation_id = path_spec["get"]["operationId"]
assert operation_id == "get_resource"

```

**Note**: This requires you to use different function names for each
endpoint/method combination, or you will end up with a conflicting
`operationId`s. But this is usually pretty easy to ensure, and can significantly
improve the naming used by your auto-generated API client(s).

### Inferring

If you know that you want to use the annotated return type as the
`response_model` (for serialization purposes _or_ for OpenAPI spec generation),
you can use a `authx_core.authxInferring` in place of an `APIRouter`, and the
`response_model` will be automatically extracted from the annotated return type.

As you can see below, by default, no response schema is generated when you don't
specify a `response_model`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/default")
def get_resource(resource_id: int) -> str:
    # the response will be serialized as a JSON number, *not* a string
    return resource_id


def get_response_schema(openapi_spec, endpoint_path):
    responses = openapi_spec["paths"][endpoint_path]["get"]["responses"]
    return responses["200"]["content"]["application/json"]["schema"]


openapi_spec = app.openapi()
assert get_response_schema(openapi_spec, "/default") == {}

```

However, using `authxInferring`, a response schema _is_ generated by default:

```python
from fastapi import FastAPI

from authx_core import authxInferring

app = FastAPI()


@app.get("/default")
def get_resource(resource_id: int) -> str:
    # the response will be serialized as a JSON number, *not* a string
    return resource_id


router = authxInferring()


@router.get("/inferred")
def get_resource(resource_id: int) -> str:
    return resource_id


app.include_router(router)


def get_response_schema(openapi_spec, endpoint_path):
    responses = openapi_spec["paths"][endpoint_path]["get"]["responses"]
    return responses["200"]["content"]["application/json"]["schema"]


openapi_spec = app.openapi()
assert get_response_schema(openapi_spec, "/default") == {}
assert get_response_schema(openapi_spec, "/inferred")["type"] == "string"

```

Behind the scenes, what happens is precisely equivalent to what would happen if
you passed the annotated return type as the `response_model` argument to the
endpoint decorator. So the annotated return type will also be used for
serialization, etc.

Note that `authxInferring` has precisely the same API for all methods as a
regular `APIRouter`, and you can still manually override the provided
`response_model` if desired.

## 0.0.2

The `authx_core.middleware` module provides basic profiling functionality that
could be used to find performance bottlenecks, monitor for regressions, etc.

There are currently two public functions provided by this module:

- `authxMiddleware`, which can be used to add a middleware to a `FastAPI` app
  that will log very basic profiling information for each request (with low
  overhead).

- `authxRecord`, which can be called on a `starlette.requests.Request` instance
  for a `FastAPI` app with the timing middleware installed (via
  `authxMiddleware`), and will emit performance information for the request at
  the point at which it is called.

## 0.0.1

### Features

Utilities to help reduce boilerplate and reuse common functionality, Based to
Support Building of [Authx](https://authx.yezz.me) &amp; Authx-lite ⚡:

- **SQLAlchemy Sessions**: The `AuthxDB` class provides an easily-customized
  SQLAlchemy Session dependency.

It also adds a variety of more basic utilities that are useful across a wide
variety of projects:

- **GUID Type**: The provided GUID type makes it easy to use UUIDs as the
  primary keys for your database tables
