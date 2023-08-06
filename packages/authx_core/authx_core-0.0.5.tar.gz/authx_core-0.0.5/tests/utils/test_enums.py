from enum import auto

from authx_core.utils import authxCamelStrEnum, authxStrEnum


def test_str_enum() -> None:
    class MyStrEnum(authxStrEnum):
        choice_one = auto()
        choice_two = auto()

    values = [x.value for x in MyStrEnum]
    assert values == ["choice_one", "choice_two"]


def test_camel_str_enum() -> None:
    class MyCamelStrEnum(authxCamelStrEnum):
        choice_one = auto()
        choice_two = auto()

    values = [x.value for x in MyCamelStrEnum]
    assert values == ["choiceOne", "choiceTwo"]
