from typing import TYPE_CHECKING, Any, Dict, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.sql.base import ImmutableColumnCollection

from authx_core.utils import authxCamel

T = TypeVar("T", bound="CustomBase")


class CustomMeta(DeclarativeMeta):
    __table__: sa.Table

    @property
    def columns(cls) -> ImmutableColumnCollection:
        return cls.__table__.columns


class CustomBase:
    __table__: sa.Table

    if TYPE_CHECKING:
        __tablename__: str
    else:

        @declared_attr
        def __tablename__(cls) -> str:
            return authxCamel(cls.__name__)

    def dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self.__table__.c.keys()}


_Base = declarative_base(cls=CustomBase, metaclass=CustomMeta)
if TYPE_CHECKING:

    class Base(_Base, CustomBase, metaclass=CustomMeta):
        __table__: sa.Table
        __tablename_: str
        metadata: sa.MetaData
        columns: ImmutableColumnCollection
        if not False:  # pragma: no cover

            def __init__(self, **kwargs: Any) -> None:
                pass

        def dict(self) -> Dict[str, Any]:
            ...

else:
    exec("Base = _Base")
S = TypeVar("S", bound="Base")


def add_base(session: Session, item: S) -> S:
    session.add(item)
    session.commit()
    return item
