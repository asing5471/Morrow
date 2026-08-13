"""Network-related security checks for Morrow."""

import ipaddress
from urllib.parse import urlparse


ALLOWED_SCHEMES = {"http", "https"}


def is_allowed_scheme(scheme: str) -> bool:
    """Return True when the URL scheme is allowed for browser navigation."""
    return scheme.lower() in ALLOWED_SCHEMES


def is_public_ip_address(host: str) -> bool:
    """Return True when a literal IP address is globally reachable."""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        # The host is a domain name rather than a literal IP address.
        return True

    return (
        address.is_global
        and not address.is_loopback
        and not address.is_private
        and not address.is_link_local
        and not address.is_reserved
        and not address.is_unspecified
    )


def is_safe_hostname(hostname: str) -> bool:
    """Return True when a hostname is safe under the current checks."""
    hostname = hostname.lower().rstrip(".")

    if hostname == "localhost":
        return False

    return is_public_ip_address(hostname)


def is_valid_navigation_url(url: str) -> bool:
    """Return True when a URL is suitable for browser navigation."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if not is_allowed_scheme(parsed.scheme):
        return False

    if not parsed.hostname:
        return False

    return is_safe_hostname(parsed.hostname)
