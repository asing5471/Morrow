"""Morrow application entry point."""

from fastapi import FastAPI

from backend.api.sessions import router as sessions_router


app = FastAPI(
    title="Morrow",
    description="Private, local-first browser infrastructure.",
    version="0.1.0",
)

app.include_router(sessions_router)
