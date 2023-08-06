from functools import lru_cache
from typing import Any, Dict

from pydantic import BaseSettings


class _settings(BaseSettings):
    """This class enables the configuration of your FastAPI instance through the use of environment variables."""

    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI"
    version: str = "0.0.1"

    # Custom settings
    disable_docs: bool = False
    disable_superuser_dependency: bool = False
    include_admin_routes: bool = False
    main_router_prefix: str = "/api/v1"

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        """
        This returns a dictionary of the most commonly used keyword arguments when initializing a FastAPI instance

        If `self.disable_docs` is True, the various docs-related arguments are disabled, preventing your spec from being
        published.
        """
        fastapi_kwargs: Dict[str, Any] = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
        if self.disable_docs:
            fastapi_kwargs.update(
                {"docs_url": None, "openapi_url": None, "redoc_url": None}
            )
        return fastapi_kwargs

    class Config:
        env_prefix = "api_"
        validate_assignment = True


@lru_cache()
def _api_settings() -> _settings:
    return _settings()
