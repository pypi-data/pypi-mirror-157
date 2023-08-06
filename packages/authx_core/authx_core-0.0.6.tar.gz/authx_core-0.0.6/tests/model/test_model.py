from dataclasses import dataclass

from authx_core import authxModel


def test_orm_mode() -> None:
    @dataclass
    class Data:
        x: int

    class Model(authxModel):
        x: int

    assert Model.from_orm(Data(x=1)).x == 1


def test_alias() -> None:
    class Model(authxModel):
        some_field: str

    assert Model(some_field="a").some_field == "a"
    assert Model(someField="a").some_field == "a"  # type: ignore[call-arg]
