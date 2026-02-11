"""FastAPI dependency injection for shared resources."""

from __future__ import annotations

from smae.api.db import DashboardDB

_db: DashboardDB | None = None


def get_db() -> DashboardDB:
    """Return the singleton DB instance. Initialised at app startup."""
    assert _db is not None, "Database not initialised — call init_db first"
    return _db


async def init_db(db: DashboardDB) -> None:
    global _db
    _db = db
    await _db.connect()


async def close_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None
