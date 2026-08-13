"""Tests for Morrow browser session management."""

import pytest
from playwright.async_api import async_playwright

from backend.browser.manager import BrowserSessionManager


@pytest.mark.asyncio
async def test_create_session() -> None:
    """A new session should launch a browser and create a page."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()

        assert session.id
        assert manager.get_session(session.id) is session
        assert session.browser.is_connected()
        assert not session.page.is_closed()

        await manager.close_all()


@pytest.mark.asyncio
async def test_session_ids_are_unique() -> None:
    """Each newly created session should receive a unique ID."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        first = await manager.create_session()
        second = await manager.create_session()

        assert first.id != second.id

        await manager.close_all()


@pytest.mark.asyncio
async def test_remove_session() -> None:
    """Removing a session should close its browser and stop tracking it."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()
        removed = await manager.remove_session(session.id)

        assert removed is session
        assert manager.get_session(session.id) is None
        assert not session.browser.is_connected()

        await manager.close_all()


@pytest.mark.asyncio
async def test_remove_missing_session() -> None:
    """Removing an unknown session should return None."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        removed = await manager.remove_session("does-not-exist")

        assert removed is None

        await manager.close_all()


@pytest.mark.asyncio
async def test_navigate() -> None:
    """A session should be able to navigate its page to a URL."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()
        await session.navigate("https://example.com")

        assert session.page.url == "https://example.com/"

        await manager.close_all()
