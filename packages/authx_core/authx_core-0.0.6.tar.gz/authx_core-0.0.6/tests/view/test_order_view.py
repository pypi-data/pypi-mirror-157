from fastapi import APIRouter, FastAPI
from starlette.testclient import TestClient

from authx_core import AuthXBasedView


def test_order_view() -> None:
    router = APIRouter()

    @AuthXBasedView(router)
    class test_view:
        @router.get("/test")
        def get_test(self) -> int:
            return 1

        @router.get("/{item_id}")
        def get_item(self) -> int:
            return 2

    app = FastAPI()
    app.include_router(router)

    assert TestClient(app).get("/test").json() == 1
    assert TestClient(app).get("/other").json() == 2
