"""Threshold endpoints — definitions and current status."""

from __future__ import annotations

from fastapi import APIRouter

from smae.api.deps import get_db
from smae.api.models import ThresholdDefinitionResponse
from smae.models.enums import ThresholdStatus
from smae.models.thresholds import ALL_THRESHOLDS

router = APIRouter(tags=["thresholds"])


@router.get("/thresholds", response_model=list[ThresholdDefinitionResponse])
async def list_thresholds() -> list[ThresholdDefinitionResponse]:
    return [
        ThresholdDefinitionResponse(
            name=t.name,
            category=t.category.value,
            description=t.description,
            networks=[n.value for n in t.networks],
            threshold_value=t.threshold_value,
            unit=t.unit,
        )
        for t in ALL_THRESHOLDS
    ]


@router.get("/thresholds/status")
async def threshold_status() -> list[dict]:
    """Return current threshold crossing status from the latest pipeline run."""
    db = get_db()
    events, _ = await db.get_events(limit=500)
    crossings = []
    for event in events:
        for tc in event.threshold_crossings:
            crossings.append({
                "event_id": event.id,
                "event_title": event.title,
                "metric_name": tc.metric.name,
                "category": tc.metric.category.value,
                "baseline_value": tc.metric.baseline_value,
                "baseline_date": tc.metric.baseline_date.isoformat(),
                "delta": tc.metric.delta,
                "current_value": tc.metric.current_value,
                "threshold_value": tc.metric.threshold_value,
                "unit": tc.metric.unit,
                "status": tc.metric.status.value,
                "alert_level": tc.alert_level.value,
                "comparison": tc.metric.comparison_string,
            })
    return crossings
