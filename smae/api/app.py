"""FastAPI application factory for the SMAE dashboard API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from smae.api.db import DashboardDB
from smae.api.deps import close_db, init_db
from smae.api.routers import convergence, events, networks, pipeline, reports, thresholds


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db = DashboardDB()
    await init_db(db)
    yield
    await close_db()


def create_app(*, static_dir: Path | None = None) -> FastAPI:
    app = FastAPI(
        title="SMAE Dashboard API",
        description="Socio-Metabolic Analytical Engine — web dashboard backend",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(events.router, prefix="/api/v1")
    app.include_router(thresholds.router, prefix="/api/v1")
    app.include_router(convergence.router, prefix="/api/v1")
    app.include_router(networks.router, prefix="/api/v1")
    app.include_router(pipeline.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")

    if static_dir and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()
