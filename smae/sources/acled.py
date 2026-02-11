"""ACLED (Armed Conflict Location & Event Data) source adapter.

Provides armed conflict event data, updated weekly. Primarily feeds
Network I (Carbon), Network IV (Mineral), and Network VIII (Labor)
analysis — resource conflicts, extractive violence, labor-related
repression, and resistance events.

Authentication: ACLED uses OAuth token-based authentication. Requires
a registered account (email + password) at acleddata.com. The adapter
obtains a 24-hour access token and refreshes automatically.
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

TOKEN_URL = "https://acleddata.com/oauth/token"
API_URL = "https://acleddata.com/api/acled/read"


class ACLEDAdapter(SourceAdapter):
    """Adapter for the ACLED conflict event database.

    Requires credentials dict with 'email' and 'password' keys,
    corresponding to a registered myACLED account.
    """

    name: ClassVar[str] = "acled"
    tier: ClassVar[SourceTier] = SourceTier.SPECIALIZED_RESEARCH
    networks: ClassVar[tuple[MetabolicNetwork, ...]] = (
        MetabolicNetwork.CARBON,
        MetabolicNetwork.MINERAL,
    )
    base_url: ClassVar[str] = API_URL

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._access_token: str | None = None

    async def _authenticate(self) -> None:
        """Obtain an OAuth access token from ACLED."""
        email = self._credentials.get("email", "")
        password = self._credentials.get("password", "")
        if not email or not password:
            raise ValueError(
                "ACLED requires 'email' and 'password' in credentials. "
                "Register at https://acleddata.com to obtain an account."
            )

        resp = await self._client.post(
            TOKEN_URL,
            data={
                "username": email,
                "password": password,
                "grant_type": "password",
                "client_id": "acled",
            },
        )
        resp.raise_for_status()
        token_data = resp.json()
        self._access_token = token_data["access_token"]

    async def _ensure_authenticated(self) -> None:
        """Authenticate if we don't have a valid token."""
        if self._access_token is None:
            await self._authenticate()

    async def fetch_events(self, since: date) -> list[Event]:
        """Fetch ACLED events since given date.

        Returns tagged Event objects with conflict data mapped to
        SMAE ontology nodes and metabolic networks.
        """
        await self._ensure_authenticated()

        params = {
            "event_date": since.isoformat(),
            "event_date_where": ">=",
            "limit": 500,
        }
        headers = {"Authorization": f"Bearer {self._access_token}"}

        resp = await self._client.get(self.base_url, params=params, headers=headers)

        # Re-authenticate on 401 and retry once
        if resp.status_code == 401:
            await self._authenticate()
            headers["Authorization"] = f"Bearer {self._access_token}"
            resp = await self._client.get(self.base_url, params=params, headers=headers)

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

        # Extend network tagging based on event content
        networks = list(self.networks)
        notes_lower = record.get("notes", "").lower()
        if any(kw in notes_lower for kw in ("labor", "labour", "worker", "mine ", "mining")):
            if MetabolicNetwork.LABOR not in networks:
                networks.append(MetabolicNetwork.LABOR)

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
            networks=networks,
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
