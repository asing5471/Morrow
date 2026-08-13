"""Application configuration for Morrow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Morrow server."""

    host: str = "127.0.0.1"
    port: int = 3000


settings = Settings()
