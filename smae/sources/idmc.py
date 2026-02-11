"""IDMC (Internal Displacement Monitoring Centre) source adapter.

Provides internal displacement data, updated quarterly with event alerts.
Feeds displacement analysis across all five metabolic networks.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import ClassVar

from smae.models.enums import (
    AlertLevel,
    AnalyticalLayer,
    MetabolicNetwork,
    OntologyNode,
    SourceTier,
    ThresholdCategory,
    ThresholdStatus,
)
from smae.models.events import Event, Source, ThresholdCrossing, ThresholdMetric
from smae.sources.base import SourceAdapter


class IDMCAdapter(SourceAdapter):
    """Adapter for IDMC displacement data."""

    name: ClassVar[str] = "idmc"
    tier: ClassVar[SourceTier] = SourceTier.UN_OPERATIONAL
    networks: ClassVar[tuple[MetabolicNetwork, ...]] = tuple(MetabolicNetwork)
    base_url: ClassVar[str] = "https://api.idmcdb.org/api"

    async def fetch_events(self, since: date) -> list[Event]:
        """Fetch IDMC displacement events since given date."""
        endpoint = f"{self.base_url}/displacement_data"
        params = {
            "ci": "IDMC",
            "year": since.year,
        }
        if self._api_key:
            params["key"] = self._api_key

        resp = await self._client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()

        events = []
        for record in data.get("results", []):
            event = self._map_record(record, since)
            if event:
                events.append(event)
        return events

    def _map_record(self, record: dict, since: date) -> Event | None:
        """Map an IDMC record to an SMAE Event."""
        country = record.get("country", "Unknown")
        iso3 = record.get("iso3", "")
        conflict_displaced = record.get("conflict_new_displacements", 0) or 0
        disaster_displaced = record.get("disaster_new_displacements", 0) or 0
        total = conflict_displaced + disaster_displaced

        if total == 0:
            return None

        year = record.get("year", since.year)
        event_date = date(year, 1, 1)

        # Check displacement bright-line threshold
        crossings = []
        if total > 100_000:
            crossings.append(ThresholdCrossing(
                metric=ThresholdMetric(
                    name="displacement_single_event",
                    category=ThresholdCategory.ABSOLUTE,
                    networks=list(MetabolicNetwork),
                    baseline_value=0,
                    baseline_date=date(year - 1, 1, 1),
                    delta=float(total),
                    current_value=float(total),
                    threshold_value=100_000,
                    unit="persons",
                    status=ThresholdStatus.EXCEEDED,
                ),
                detected_at=datetime.now(),
                alert_level=(
                    AlertLevel.CRITICAL if total > 500_000 else AlertLevel.ALERT  # noqa: F821
                ),
            ))

        return Event(
            id=f"idmc-{iso3}-{year}",
            title=f"Internal displacement: {country} ({year})",
            summary=(
                f"{country}: {total:,} new internal displacements in {year} "
                f"(conflict: {conflict_displaced:,}, disaster: {disaster_displaced:,})."
            ),
            event_date=event_date,
            detected_at=datetime.now(),
            country=country,
            networks=list(self.networks),
            layers=[AnalyticalLayer.EXTERNALITY, AnalyticalLayer.FLOW],
            nodes=[OntologyNode.DISPLACEMENT],
            threshold_crossings=crossings,
            sources=[
                Source(
                    organization="IDMC",
                    report_name=f"Global Internal Displacement Database — {country} {year}",
                    tier=self.tier,
                    access_date=date.today(),
                )
            ],
        )
