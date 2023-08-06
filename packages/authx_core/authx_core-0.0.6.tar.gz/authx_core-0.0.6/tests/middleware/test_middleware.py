import pytest
from fastapi import FastAPI
from starlette.requests import Request
from starlette.testclient import TestClient

from authx_core import authxRecord

app = FastAPI()


@app.get("/")
def fail_to_record(request: Request) -> None:
    authxRecord(request)


client3 = TestClient(app)


def test_recording_fails_without_middleware() -> None:
    with pytest.raises(ValueError) as exc_info:
        client3.get("/")
    assert str(exc_info.value) == "No timer present on request"
