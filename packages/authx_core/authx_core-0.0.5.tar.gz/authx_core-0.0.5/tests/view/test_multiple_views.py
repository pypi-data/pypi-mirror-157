from typing import Any

from fastapi import APIRouter
from starlette.testclient import TestClient

from authx_core import AuthXBasedView


def test_multiple_views() -> None:
    router = APIRouter()

    @AuthXBasedView(router)
    class RootHandler:
        @router.get("/items/?")
        @router.get("/items/{item_path:path}")
        @router.get("/database/{item_path:path}")
        def root(self, item_path: str = None, item_query: str = None) -> Any:
            if item_path:
                return {"item_path": item_path}
            if item_query:
                return {"item_query": item_query}  # pragma: no cover
            return []

    client = TestClient(router)

    assert client.get("/items").json() == []
    assert client.get("/items/1").json() == {"item_path": "1"}
    assert client.get("/database/abc").json() == {"item_path": "abc"}
