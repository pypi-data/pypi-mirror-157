from pydantic import BaseSettings


class _base(BaseSettings):
    """Base settings for the application."""

    class Config:
        env_prefix = ""
        arbitrary_types_allowed = True
        validate_assignment = True
