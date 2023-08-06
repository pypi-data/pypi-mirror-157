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
    """
    This function returns a cached instance of the `_settings` object.

    Caching is used to prevent re-reading the environment every time the API settings are used in an endpoint.

    If you want to change an environment variable and reset the cache (e.g., during testing), this can be done
    using the `lru_cache` instance method `_api_settings.cache_clear()`.
    """
    return _settings()
