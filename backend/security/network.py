"""Network-related security checks for Morrow."""

import asyncio
import ipaddress
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}


def is_allowed_scheme(scheme: str) -> bool:
    """Return True when the URL scheme is allowed for browser navigation."""
    return scheme.lower() in ALLOWED_SCHEMES


def is_public_ip_address(host: str) -> bool:
    """Return True when an IP address is globally reachable."""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False

    return (
        address.is_global
        and not address.is_loopback
        and not address.is_private
        and not address.is_link_local
        and not address.is_reserved
        and not address.is_unspecified
    )


def is_safe_hostname(hostname: str) -> bool:
    """Return True when a hostname is syntactically safe to resolve."""
    hostname = hostname.lower().rstrip(".")

    if not hostname or hostname == "localhost":
        return False

    return True


def is_valid_navigation_url(url: str) -> bool:
    """Return True when a URL passes local navigation checks."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if not is_allowed_scheme(parsed.scheme):
        return False

    if not parsed.hostname:
        return False

    return is_safe_hostname(parsed.hostname)


async def resolve_hostname(hostname: str) -> list[str]:
    """Resolve a hostname and return its resolved IP addresses."""
    addresses = await asyncio.get_running_loop().getaddrinfo(
        hostname,
        None,
        type=0,
    )

    return list(dict.fromkeys(address[4][0] for address in addresses))


async def is_safe_navigation_url(url: str) -> bool:
    """Return True when a URL passes navigation and DNS security checks."""
    if not is_valid_navigation_url(url):
        return False

    parsed = urlparse(url)
    hostname = parsed.hostname

    if hostname is None:
        return False

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return is_public_ip_address(hostname)

    try:
        addresses = await resolve_hostname(hostname)
    except OSError:
        return False

    if not addresses:
        return False

    return all(is_public_ip_address(address) for address in addresses)
