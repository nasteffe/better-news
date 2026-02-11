"""Global Forest Watch (GFW) source adapter.

Provides near-real-time deforestation alerts and forest change data.
Feeds Network I (Carbon) and Network III (Soil) analysis.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import ClassVar

from smae.models.enums import (
    AnalyticalLayer,
    MetabolicNetwork,
    OntologyNode,
    SourceTier,
)
from smae.models.events import Event, Source
from smae.sources.base import SourceAdapter


class GFWAdapter(SourceAdapter):
    """Adapter for the Global Forest Watch deforestation alert system."""

    name: ClassVar[str] = "gfw"
    tier: ClassVar[SourceTier] = SourceTier.SPECIALIZED_RESEARCH
    networks: ClassVar[tuple[MetabolicNetwork, ...]] = (
        MetabolicNetwork.CARBON,
        MetabolicNetwork.SOIL,
    )
    base_url: ClassVar[str] = "https://data-api.globalforestwatch.org"

    async def fetch_events(self, since: date) -> list[Event]:
        """Fetch GFW deforestation alerts since given date.

        Queries the GLAD alert system for significant deforestation events
        and maps them to SMAE events with network/layer tagging.
        """
        endpoint = f"{self.base_url}/dataset/gfw_integrated_alerts/latest/query"
        params = {
            "sql": (
                f"SELECT * FROM data "
                f"WHERE alert__date >= '{since.isoformat()}' "
                f"AND alert__count > 100 "
                f"ORDER BY alert__date DESC LIMIT 200"
            ),
        }
        headers = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        resp = await self._client.get(endpoint, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        events = []
        for record in data.get("data", []):
            event = self._map_record(record)
            if event:
                events.append(event)
        return events

    def _map_record(self, record: dict) -> Event | None:
        """Map a GFW alert record to an SMAE Event."""
        alert_date_str = record.get("alert__date", "")
        try:
            alert_date = date.fromisoformat(alert_date_str)
        except (ValueError, TypeError):
            return None

        country = record.get("iso", "Unknown")
        alert_count = record.get("alert__count", 0)
        area_ha = record.get("area__ha", 0)

        return Event(
            id=f"gfw-{country}-{alert_date_str}",
            title=f"Deforestation alert: {country}",
            summary=(
                f"{alert_count} deforestation alerts detected in {country}, "
                f"covering approximately {area_ha:,.0f} ha. "
                f"Detected via GLAD integrated alert system."
            ),
            event_date=alert_date,
            detected_at=datetime.now(),
            country=country,
            networks=list(self.networks),
            layers=[AnalyticalLayer.FLOW, AnalyticalLayer.STOCK],
            nodes=[OntologyNode.APPROPRIATION],
            sources=[
                Source(
                    organization="Global Forest Watch",
                    report_name=f"GLAD Alert — {country} — {alert_date_str}",
                    tier=self.tier,
                    access_date=date.today(),
                )
            ],
        )
