"""SQLite persistence layer for SMAE dashboard state.

Stores pipeline run results so the dashboard can browse events, thresholds,
and convergence data between pipeline runs.  Uses aiosqlite for async access
and serialises Pydantic models as JSON.
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import aiosqlite

from smae.models.convergence import ConvergenceScore
from smae.models.events import Event

DEFAULT_DB_PATH = Path("smae_dashboard.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id          TEXT PRIMARY KEY,
    run_date    TEXT NOT NULL,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    status      TEXT NOT NULL DEFAULT 'running',
    events_ingested     INTEGER DEFAULT 0,
    threshold_crossings INTEGER DEFAULT 0,
    convergence_nodes   INTEGER DEFAULT 0,
    source_errors       TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS events (
    id          TEXT PRIMARY KEY,
    run_id      TEXT NOT NULL REFERENCES pipeline_runs(id),
    data        TEXT NOT NULL,
    event_date  TEXT NOT NULL,
    country     TEXT NOT NULL,
    alert_level TEXT NOT NULL,
    ci_score    INTEGER NOT NULL DEFAULT 1,
    networks    TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_events_run      ON events(run_id);
CREATE INDEX IF NOT EXISTS idx_events_date     ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_country  ON events(country);
CREATE INDEX IF NOT EXISTS idx_events_alert    ON events(alert_level);

CREATE TABLE IF NOT EXISTS convergence_scores (
    event_id TEXT PRIMARY KEY,
    run_id   TEXT NOT NULL REFERENCES pipeline_runs(id),
    data     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id         TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    report_type TEXT NOT NULL,
    filename   TEXT NOT NULL,
    path       TEXT NOT NULL
);
"""


class DashboardDB:
    """Async SQLite wrapper for dashboard persistence."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(str(self._db_path))
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA_SQL)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        assert self._conn is not None, "Database not connected"
        return self._conn

    # --- Pipeline runs ---

    async def start_pipeline_run(self) -> str:
        run_id = uuid.uuid4().hex[:12]
        await self.conn.execute(
            "INSERT INTO pipeline_runs (id, run_date, started_at, status) VALUES (?, ?, ?, ?)",
            (run_id, date.today().isoformat(), datetime.utcnow().isoformat(), "running"),
        )
        await self.conn.commit()
        return run_id

    async def finish_pipeline_run(
        self,
        run_id: str,
        *,
        status: str = "completed",
        events_ingested: int = 0,
        threshold_crossings: int = 0,
        convergence_nodes: int = 0,
        source_errors: list[str] | None = None,
    ) -> None:
        await self.conn.execute(
            """UPDATE pipeline_runs
               SET finished_at = ?, status = ?,
                   events_ingested = ?, threshold_crossings = ?,
                   convergence_nodes = ?, source_errors = ?
               WHERE id = ?""",
            (
                datetime.utcnow().isoformat(),
                status,
                events_ingested,
                threshold_crossings,
                convergence_nodes,
                json.dumps(source_errors or []),
                run_id,
            ),
        )
        await self.conn.commit()

    async def get_pipeline_runs(self, limit: int = 20) -> list[dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def get_latest_run(self) -> dict | None:
        cursor = await self.conn.execute(
            "SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    # --- Events ---

    async def store_events(self, run_id: str, events: list[Event]) -> None:
        rows = [
            (
                e.id,
                run_id,
                e.model_dump_json(),
                e.event_date.isoformat(),
                e.country,
                e.alert_level.value,
                e.convergence_index,
                json.dumps([n.value for n in e.networks]),
            )
            for e in events
        ]
        await self.conn.executemany(
            """INSERT OR REPLACE INTO events
               (id, run_id, data, event_date, country, alert_level, ci_score, networks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        await self.conn.commit()

    async def get_events(
        self,
        *,
        network: int | None = None,
        alert_level: str | None = None,
        country: str | None = None,
        since: date | None = None,
        until: date | None = None,
        min_ci: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Event], int]:
        conditions: list[str] = []
        params: list[object] = []

        if network is not None:
            conditions.append("networks LIKE ?")
            params.append(f"%{network}%")
        if alert_level is not None:
            conditions.append("alert_level = ?")
            params.append(alert_level)
        if country is not None:
            conditions.append("country LIKE ?")
            params.append(f"%{country}%")
        if since is not None:
            conditions.append("event_date >= ?")
            params.append(since.isoformat())
        if until is not None:
            conditions.append("event_date <= ?")
            params.append(until.isoformat())
        if min_ci is not None:
            conditions.append("ci_score >= ?")
            params.append(min_ci)

        where = " AND ".join(conditions) if conditions else "1=1"

        count_cursor = await self.conn.execute(
            f"SELECT COUNT(*) FROM events WHERE {where}", params
        )
        total = (await count_cursor.fetchone())[0]

        cursor = await self.conn.execute(
            f"SELECT data FROM events WHERE {where} ORDER BY event_date DESC LIMIT ? OFFSET ?",
            [*params, limit, offset],
        )
        rows = await cursor.fetchall()
        events = [Event.model_validate_json(r[0]) for r in rows]
        return events, total

    async def get_event(self, event_id: str) -> Event | None:
        cursor = await self.conn.execute(
            "SELECT data FROM events WHERE id = ?", (event_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Event.model_validate_json(row[0])

    # --- Convergence scores ---

    async def store_convergence_scores(
        self, run_id: str, scores: list[ConvergenceScore]
    ) -> None:
        rows = [
            (cs.event_id, run_id, cs.model_dump_json())
            for cs in scores
        ]
        await self.conn.executemany(
            "INSERT OR REPLACE INTO convergence_scores (event_id, run_id, data) VALUES (?, ?, ?)",
            rows,
        )
        await self.conn.commit()

    async def get_convergence_scores(self) -> list[ConvergenceScore]:
        cursor = await self.conn.execute("SELECT data FROM convergence_scores")
        rows = await cursor.fetchall()
        return [ConvergenceScore.model_validate_json(r[0]) for r in rows]

    # --- Reports ---

    async def store_report(
        self, report_type: str, filename: str, path: str
    ) -> str:
        report_id = uuid.uuid4().hex[:12]
        await self.conn.execute(
            "INSERT INTO reports (id, created_at, report_type, filename, path) VALUES (?, ?, ?, ?, ?)",
            (report_id, datetime.utcnow().isoformat(), report_type, filename, path),
        )
        await self.conn.commit()
        return report_id

    async def get_reports(self, limit: int = 50) -> list[dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
