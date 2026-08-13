"""Application configuration for Morrow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServerSettings:
    """Runtime settings for the Morrow server."""

    host: str = "127.0.0.1"
    port: int = 3000


@dataclass(frozen=True)
class BrowserSettings:
    """Default browser behavior for Morrow sessions."""

    headless: bool = True


@dataclass(frozen=True)
class SecuritySettings:
    """Default security restrictions for Morrow."""

    allow_remote_access: bool = False
    allow_file_access: bool = False
    allow_downloads: bool = False
    allow_uploads: bool = False
    allow_clipboard: bool = False


@dataclass(frozen=True)
class Settings:
    """Complete Morrow runtime configuration."""

    server: ServerSettings = ServerSettings()
    browser: BrowserSettings = BrowserSettings()
    security: SecuritySettings = SecuritySettings()


settings = Settings()
