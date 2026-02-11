"""Network endpoints — summaries and per-network detail."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from smae.api.deps import get_db
from smae.api.models import NetworkSummary
from smae.models.enums import AlertLevel, MetabolicNetwork

router = APIRouter(tags=["networks"])


def _max_alert(levels: list[AlertLevel]) -> str:
    order = list(AlertLevel)
    if not levels:
        return AlertLevel.WATCH.value
    return max(levels, key=lambda a: order.index(a)).value


@router.get("/networks", response_model=list[NetworkSummary])
async def list_networks() -> list[NetworkSummary]:
    db = get_db()
    events, _ = await db.get_events(limit=1000)

    summaries = []
    for net in MetabolicNetwork:
        net_events = [e for e in events if net in e.networks]
        convergent = [e for e in net_events if e.convergence_index >= 2]
        crossings = sum(len(e.threshold_crossings) for e in net_events)
        summaries.append(NetworkSummary(
            network_id=net.value,
            roman=net.roman,
            label=net.label,
            event_count=len(net_events),
            convergent_count=len(convergent),
            threshold_crossings=crossings,
            max_alert=_max_alert([e.alert_level for e in net_events]),
        ))
    return summaries


@router.get("/networks/{network_id}")
async def get_network(network_id: int) -> dict:
    try:
        net = MetabolicNetwork(network_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Network not found")

    db = get_db()
    events, _ = await db.get_events(network=network_id, limit=200)

    layers: dict[str, list[dict]] = {}
    for event in events:
        for layer in event.layers:
            layers.setdefault(layer.value, []).append({
                "id": event.id,
                "title": event.title,
                "country": event.country,
                "alert_level": event.alert_level.value,
                "event_date": event.event_date.isoformat(),
            })

    resistance_events = [
        {
            "id": e.id,
            "title": e.title,
            "country": e.country,
            "resistance_summary": e.resistance_summary,
        }
        for e in events
        if e.resistance_summary and "[PENDING]" not in e.resistance_summary
    ]

    return {
        "network_id": net.value,
        "roman": net.roman,
        "label": net.label,
        "event_count": len(events),
        "layers": layers,
        "resistance_spotlight": resistance_events[:10],
    }
