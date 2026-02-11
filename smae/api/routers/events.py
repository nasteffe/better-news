"""Event endpoints — list, filter, and retrieve analytical events."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from smae.api.deps import get_db
from smae.api.models import PaginatedResponse
from smae.models.events import Event

router = APIRouter(tags=["events"])


@router.get("/events", response_model=PaginatedResponse[Event])
async def list_events(
    network: Optional[list[int]] = Query(None),
    alert_level: Optional[list[str]] = Query(None),
    country: Optional[str] = None,
    since: Optional[date] = None,
    until: Optional[date] = None,
    coupling_pattern: Optional[list[int]] = Query(None),
    min_ci: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[Event]:
    db = get_db()
    # Use first network filter for the DB query; further filtering done in-memory
    network_filter = network[0] if network else None
    alert_filter = alert_level[0] if alert_level else None

    events, total = await db.get_events(
        network=network_filter,
        alert_level=alert_filter,
        country=country,
        since=since,
        until=until,
        min_ci=min_ci,
        limit=limit,
        offset=offset,
    )

    # In-memory filtering for multi-value params the DB layer doesn't handle
    if network and len(network) > 1:
        net_set = set(network)
        events = [e for e in events if net_set & {n.value for n in e.networks}]
    if alert_level and len(alert_level) > 1:
        al_set = set(alert_level)
        events = [e for e in events if e.alert_level.value in al_set]
    if coupling_pattern:
        cp_set = set(coupling_pattern)
        events = [e for e in events if cp_set & {p.value for p in e.coupling_patterns}]

    return PaginatedResponse(items=events, total=total, limit=limit, offset=offset)


@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str) -> Event:
    db = get_db()
    event = await db.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
