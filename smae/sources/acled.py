"""ACLED (Armed Conflict Location & Event Data) source adapter.

Provides armed conflict event data, updated weekly. Primarily feeds
Network I (Carbon) and Network IV (Mineral) analysis — resource conflicts,
extractive violence, and resistance events.
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


class ACLEDAdapter(SourceAdapter):
    """Adapter for the ACLED conflict event database."""

    name: ClassVar[str] = "acled"
    tier: ClassVar[SourceTier] = SourceTier.SPECIALIZED_RESEARCH
    networks: ClassVar[tuple[MetabolicNetwork, ...]] = (
        MetabolicNetwork.CARBON,
        MetabolicNetwork.MINERAL,
    )
    base_url: ClassVar[str] = "https://api.acleddata.com/acled/read"

    async def fetch_events(self, since: date) -> list[Event]:
        """Fetch ACLED events since given date.

        Returns tagged Event objects with conflict data mapped to
        SMAE ontology nodes and metabolic networks.
        """
        params = {
            "event_date": since.isoformat(),
            "event_date_where": ">=",
            "limit": 500,
        }
        if self._api_key:
            params["key"] = self._api_key

        resp = await self._client.get(self.base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

        events = []
        for record in data.get("data", []):
            event = self._map_record(record)
            if event:
                events.append(event)
        return events

    def _map_record(self, record: dict) -> Event | None:
        """Map an ACLED record to an SMAE Event."""
        event_type = record.get("event_type", "")
        sub_event = record.get("sub_event_type", "")

        # Determine ontology nodes based on ACLED event type
        nodes = [OntologyNode.APPROPRIATION]
        if "protest" in event_type.lower() or "riot" in event_type.lower():
            nodes = [OntologyNode.RESISTANCE]
        elif "violence against civilians" in event_type.lower():
            nodes = [OntologyNode.DISPLACEMENT]

        # Determine layers
        layers = [AnalyticalLayer.FLOW]
        if "government" in record.get("actor1", "").lower():
            layers.append(AnalyticalLayer.GOVERNANCE)

        country = record.get("country", "Unknown")
        event_date_str = record.get("event_date", "")

        try:
            event_date = date.fromisoformat(event_date_str)
        except (ValueError, TypeError):
            return None

        fatalities = int(record.get("fatalities", 0))

        return Event(
            id=f"acled-{record.get('data_id', 'unknown')}",
            title=f"{event_type}: {sub_event}" if sub_event else event_type,
            summary=(
                f"{event_type} in {record.get('admin1', country)}, {country}. "
                f"{record.get('notes', '')}"
            ),
            event_date=event_date,
            detected_at=datetime.now(),
            country=country,
            region=record.get("admin1"),
            coordinates=(
                (float(record["latitude"]), float(record["longitude"]))
                if record.get("latitude") and record.get("longitude")
                else None
            ),
            networks=list(self.networks),
            layers=layers,
            nodes=nodes,
            sources=[
                Source(
                    organization="ACLED",
                    report_name=f"Event #{record.get('data_id', 'N/A')}",
                    tier=self.tier,
                    access_date=date.today(),
                )
            ],
        )
