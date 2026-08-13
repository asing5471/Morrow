"""Morrow application entry point."""

from fastapi import FastAPI


app = FastAPI(
    title="Morrow",
    description="Private, local-first browser infrastructure.",
    version="0.1.0",
)
