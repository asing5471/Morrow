"""Tests for Morrow network security checks."""

import pytest
from playwright.async_api import async_playwright

from backend.browser.manager import BrowserSessionManager
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
