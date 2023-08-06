from pathlib import Path

from _pytest.capture import CaptureFixture
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.testclient import TestClient

from authx_core import authxMiddleware

app = FastAPI()
authxMiddleware(app, exclude="untimed")
static_files_app = StaticFiles(directory=".")
app.mount(path="/static", app=static_files_app, name="static")


@app.get("/timed")
def get_timed() -> None:
    pass


@app.get("/untimed")
def get_untimed() -> None:
    pass


client = TestClient(app)


def test_timing(capsys: CaptureFixture) -> None:  # type: ignore
    client.get("/timed")
    out, err = capsys.readouterr()
    assert err == ""
    assert out.startswith("TIMING: Wall")
    assert "CPU:" in out
    assert out.endswith("test_timing.get_timed\n")


def test_silent_timing(capsys: CaptureFixture) -> None:  # type: ignore
    client.get("/untimed")
    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_mount(capsys: CaptureFixture) -> None:  # type: ignore
    basename = Path(__file__).name
    client.get(f"/static/{basename}")
    out, err = capsys.readouterr()
    assert err == ""
    assert out.startswith("TIMING:")
    assert out.endswith("StaticFiles<'static'>\n")


def test_missing(capsys: CaptureFixture) -> None:  # type: ignore
    client.get("/will-404")
    out, err = capsys.readouterr()
    assert err == ""
    assert out.startswith("TIMING:")
    assert out.endswith("<Path: /will-404>\n")
