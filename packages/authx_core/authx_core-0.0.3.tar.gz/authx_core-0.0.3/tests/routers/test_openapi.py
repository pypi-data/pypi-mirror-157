import pytest
from fastapi import FastAPI

from authx_core import authxOpenAPI


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()

    @app.get("/endpoint-path")
    def endpoint_name() -> str:  # pragma: no cover
        return ""

    return app


def test_base_spec(app: FastAPI) -> None:
    assert (
        app.openapi()["paths"]["/endpoint-path"]["get"]["operationId"]
        == "endpoint_name_endpoint_path_get"
    )


def test_authxOpenAPI_spec(app: FastAPI) -> None:
    authxOpenAPI(app)
    assert (
        app.openapi()["paths"]["/endpoint-path"]["get"]["operationId"]
        == "endpoint_name"
    )
