from _pytest.capture import CaptureFixture
from fastapi import FastAPI
from starlette.requests import Request
from starlette.testclient import TestClient

from authx_core import authxMiddleware, authxRecord

app = FastAPI()
authxMiddleware(app, prefix="app")


@app.get("/")
def get_with_intermediate_timing(request: Request) -> None:
    authxRecord(request, note="hello")


client2 = TestClient(app)


def test_intermediate(capsys: CaptureFixture) -> None:  # type: ignore
    client2.get("/")
    out, err = capsys.readouterr()
    assert err == ""
    out = out.strip().split("\n")
    assert len(out) == 2
    assert out[0].startswith("TIMING:")
    assert out[0].endswith("test_intermediate.get_with_intermediate_timing (hello)")
    assert out[1].startswith("TIMING:")
    assert out[1].endswith("test_intermediate.get_with_intermediate_timing")
