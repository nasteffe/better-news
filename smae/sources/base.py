"""Base classes and registry for SMAE data source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import ClassVar

import httpx

from smae.models.enums import MetabolicNetwork, SourceTier
from smae.models.events import Event


class SourceAdapter(ABC):
    """Abstract base class for all data source adapters.

    Each adapter connects to one external database/feed and returns
    tagged Event objects ready for the analytical pipeline.
    """

    name: ClassVar[str]
    tier: ClassVar[SourceTier]
    networks: ClassVar[tuple[MetabolicNetwork, ...]]
    base_url: ClassVar[str]

    def __init__(self, api_key: str | None = None, timeout: float = 30.0):
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    @abstractmethod
    async def fetch_events(self, since: date) -> list[Event]:
        """Fetch and tag events from this source since the given date."""
        ...

    async def __aenter__(self) -> SourceAdapter:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()


class SourceRegistry:
    """Registry of available data source adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, SourceAdapter] = {}

    def register(self, adapter: SourceAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> SourceAdapter | None:
        return self._adapters.get(name)

    def all(self) -> list[SourceAdapter]:
        return list(self._adapters.values())

    def by_network(self, network: MetabolicNetwork) -> list[SourceAdapter]:
        return [a for a in self._adapters.values() if network in a.networks]

    def by_tier(self, max_tier: SourceTier) -> list[SourceAdapter]:
        return [a for a in self._adapters.values() if a.tier <= max_tier]

    async def close_all(self) -> None:
        for adapter in self._adapters.values():
            await adapter.close()
