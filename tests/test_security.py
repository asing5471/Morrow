"""Tests for Morrow network security checks."""

import pytest
from playwright.async_api import async_playwright

from backend.browser.manager import BrowserSessionManager
from backend.security import network
from backend.security.network import is_safe_navigation_url
from backend.security.network import is_valid_navigation_url


def test_accepts_http_url() -> None:
    """HTTP URLs should be accepted."""
    assert is_valid_navigation_url("http://example.com")


def test_accepts_https_url() -> None:
    """HTTPS URLs should be accepted."""
    assert is_valid_navigation_url("https://example.com")


def test_rejects_file_url() -> None:
    """Local filesystem URLs should be rejected."""
    assert not is_valid_navigation_url("file:///etc/passwd")


def test_rejects_javascript_url() -> None:
    """JavaScript URLs should be rejected."""
    assert not is_valid_navigation_url("javascript:alert(1)")


def test_rejects_data_url() -> None:
    """Data URLs should be rejected."""
    assert not is_valid_navigation_url("data:text/html,<h1>Hello</h1>")


def test_rejects_unsupported_scheme() -> None:
    """Unsupported URL schemes should be rejected."""
    assert not is_valid_navigation_url("ftp://example.com")


def test_rejects_url_without_host() -> None:
    """URLs without a host should be rejected."""
    assert not is_valid_navigation_url("https://")


def test_rejects_localhost() -> None:
    """The localhost hostname should be rejected."""
    assert not is_valid_navigation_url("http://localhost")


def test_rejects_loopback_ipv4() -> None:
    """IPv4 loopback addresses should be rejected."""
    assert not is_valid_navigation_url("http://127.0.0.1")


def test_rejects_private_ipv4() -> None:
    """Private IPv4 addresses should be rejected."""
    assert not is_valid_navigation_url("http://192.168.1.1")
    assert not is_valid_navigation_url("http://10.0.0.1")
    assert not is_valid_navigation_url("http://172.16.0.1")


def test_rejects_link_local_ipv4() -> None:
    """IPv4 link-local addresses should be rejected."""
    assert not is_valid_navigation_url("http://169.254.169.254")


def test_rejects_loopback_ipv6() -> None:
    """IPv6 loopback addresses should be rejected."""
    assert not is_valid_navigation_url("http://[::1]")


def test_rejects_private_ipv6() -> None:
    """IPv6 private addresses should be rejected."""
    assert not is_valid_navigation_url("http://[fc00::1]")


def test_rejects_unspecified_ip_addresses() -> None:
    """Unspecified IP addresses should be rejected."""
    assert not is_valid_navigation_url("http://0.0.0.0")
    assert not is_valid_navigation_url("http://[::]")


@pytest.mark.asyncio
async def test_safe_navigation_url_accepts_public_dns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hostname resolving only to public IPs should be accepted."""

    async def fake_resolve_hostname(hostname: str) -> list[str]:
        return ["93.184.216.34"]

    monkeypatch.setattr(
        network,
        "resolve_hostname",
        fake_resolve_hostname,
    )

    assert await is_safe_navigation_url("https://example.com")


@pytest.mark.asyncio
async def test_safe_navigation_url_rejects_private_dns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hostname resolving to a private IP should be rejected."""

    async def fake_resolve_hostname(hostname: str) -> list[str]:
        return ["127.0.0.1"]

    monkeypatch.setattr(
        network,
        "resolve_hostname",
        fake_resolve_hostname,
    )

    assert not await is_safe_navigation_url("https://example.com")


@pytest.mark.asyncio
async def test_safe_navigation_url_rejects_mixed_dns_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hostname with any unsafe DNS result should be rejected."""

    async def fake_resolve_hostname(hostname: str) -> list[str]:
        return [
            "93.184.216.34",
            "192.168.1.1",
        ]

    monkeypatch.setattr(
        network,
        "resolve_hostname",
        fake_resolve_hostname,
    )

    assert not await is_safe_navigation_url("https://example.com")


@pytest.mark.asyncio
async def test_safe_navigation_url_rejects_dns_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DNS resolution failures should reject navigation."""

    async def fake_resolve_hostname(hostname: str) -> list[str]:
        raise OSError("DNS resolution failed")

    monkeypatch.setattr(
        network,
        "resolve_hostname",
        fake_resolve_hostname,
    )

    assert not await is_safe_navigation_url("https://example.com")


@pytest.mark.asyncio
async def test_navigation_rejects_file_url() -> None:
    """Browser sessions should reject file URLs."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)
        session = await manager.create_session()

        with pytest.raises(ValueError, match="Invalid navigation URL"):
            await session.navigate("file:///etc/passwd")

        await manager.close_all()


@pytest.mark.asyncio
async def test_navigation_rejects_javascript_url() -> None:
    """Browser sessions should reject JavaScript URLs."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)
        session = await manager.create_session()

        with pytest.raises(ValueError, match="Invalid navigation URL"):
            await session.navigate("javascript:alert(1)")

        await manager.close_all()


@pytest.mark.asyncio
async def test_navigation_rejects_data_url() -> None:
    """Browser sessions should reject data URLs."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)
        session = await manager.create_session()

        with pytest.raises(ValueError, match="Invalid navigation URL"):
            await session.navigate("data:text/html,<h1>Hello</h1>")

        await manager.close_all()
