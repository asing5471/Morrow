"""Network-related security checks for Morrow."""

from urllib.parse import urlparse


ALLOWED_SCHEMES = {"http", "https"}


def is_valid_navigation_url(url: str) -> bool:
    """Return True when a URL uses an allowed web scheme and has a host."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    return (
        parsed.scheme.lower() in ALLOWED_SCHEMES
        and bool(parsed.netloc)
    )
