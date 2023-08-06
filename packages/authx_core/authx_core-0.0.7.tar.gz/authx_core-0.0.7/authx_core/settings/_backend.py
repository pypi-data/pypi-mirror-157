from enum import auto

import sqlalchemy as sa

from authx_core.utils._enums import _StrEnum as authxStrEnum


class authxBackend(authxStrEnum):
    """Setup Database Backend"""

    sqlite = auto()
    postgresql = auto()

    @staticmethod
    def _from_engine(engine: sa.engine.Engine) -> "authxBackend":
        return authxBackend(engine.dialect.name)
