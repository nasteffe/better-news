"""Tests for the SMAE dashboard API endpoints."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import date, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from smae.api.app import create_app
from smae.api.db import DashboardDB
from smae.api.deps import close_db, init_db
from smae.models.convergence import ConvergenceScore
from smae.models.enums import (
    AlertLevel,
    AnalyticalLayer,
    CouplingPattern,
    MetabolicNetwork,
    OntologyNode,
    SourceTier,
    ThresholdCategory,
    ThresholdStatus,
)
from smae.models.events import Actor, Event, Source, ThresholdCrossing, ThresholdMetric


def _make_event(
    *,
    id: str = "evt-001",
    networks: list[MetabolicNetwork] | None = None,
    alert_level: AlertLevel = AlertLevel.ALERT,
    country: str = "Brazil",
    coupling_patterns: list[CouplingPattern] | None = None,
    resistance: str | None = "Community blockade at extraction site",
) -> Event:
    return Event(
        id=id,
        title=f"Test event {id}",
        summary="Large-scale deforestation in Xingu basin linked to soy expansion.",
        event_date=date(2026, 2, 1),
        detected_at=datetime(2026, 2, 2, 12, 0),
        country=country,
        region="Para",
        coordinates=(-3.5, -52.0),
        networks=networks or [MetabolicNetwork.CARBON, MetabolicNetwork.SOIL],
        layers=[AnalyticalLayer.FLOW, AnalyticalLayer.EXTERNALITY],
        nodes=[OntologyNode.APPROPRIATION, OntologyNode.DISPLACEMENT],
        coupling_patterns=coupling_patterns or [CouplingPattern.EXTRACTIVE_CASCADE],
        actors=[
            Actor(name="Cargill", actor_type="corporation", jurisdiction="US", role="extractor"),
        ],
        threshold_crossings=[
            ThresholdCrossing(
                metric=ThresholdMetric(
                    name="deforestation_anomaly",
                    category=ThresholdCategory.RATE_OF_CHANGE,
                    networks=[MetabolicNetwork.CARBON, MetabolicNetwork.SOIL],
                    baseline_value=150.0,
                    baseline_date=date(2025, 1, 1),
                    delta=200.0,
                    current_value=350.0,
                    threshold_value=300.0,
                    unit="km²",
                    status=ThresholdStatus.EXCEEDED,
                ),
                detected_at=datetime(2026, 2, 2, 12, 0),
                alert_level=AlertLevel.ALERT,
            )
        ],
        sources=[
            Source(
                organization="Amazon Watch",
                report_name="Xingu Basin Alert",
                tier=SourceTier.FRONTLINE_EJ,
                access_date=date(2026, 2, 2),
            ),
        ],
        alert_level=alert_level,
        resistance_summary=resistance,
        governance_context="Bolsonaro-era IBAMA budget cuts remain in effect",
        outlook_30d="Escalation likely",
    )


@pytest.fixture()
def db_and_client():
    """Create a temporary DB and test client."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = DashboardDB(db_path)

        app = create_app()

        # Override the dependency
        async def setup():
            await init_db(db)

        asyncio.get_event_loop().run_until_complete(setup())

        client = TestClient(app)
        yield db, client

        asyncio.get_event_loop().run_until_complete(close_db())


@pytest.fixture()
def seeded_client(db_and_client):
    """Client with sample events loaded."""
    db, client = db_and_client

    events = [
        _make_event(id="evt-001", country="Brazil", alert_level=AlertLevel.CRITICAL),
        _make_event(
            id="evt-002",
            country="DRC",
            networks=[MetabolicNetwork.MINERAL, MetabolicNetwork.LABOR],
            alert_level=AlertLevel.SYSTEMIC,
            coupling_patterns=[CouplingPattern.HUMANITARIAN_SECURITY_FEEDBACK],
            resistance="CODECO community militia resistance",
        ),
        _make_event(
            id="evt-003",
            country="Ecuador",
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.WATER, MetabolicNetwork.BIODIVERSITY],
            alert_level=AlertLevel.MONITOR,
            coupling_patterns=[CouplingPattern.DEBT_NATURE_TRAP],
            resistance=None,
        ),
    ]
    scores = [
        ConvergenceScore(event_id="evt-001", networks=events[0].networks),
        ConvergenceScore(event_id="evt-002", networks=events[1].networks),
        ConvergenceScore(event_id="evt-003", networks=events[2].networks),
    ]

    async def seed():
        run_id = await db.start_pipeline_run()
        await db.store_events(run_id, events)
        await db.store_convergence_scores(run_id, scores)
        await db.finish_pipeline_run(
            run_id, events_ingested=3, threshold_crossings=3, convergence_nodes=2
        )

    asyncio.get_event_loop().run_until_complete(seed())
    return client


# --- Event endpoints ---


class TestEventEndpoints:
    def test_list_events_empty(self, db_and_client):
        _, client = db_and_client
        resp = client.get("/api/v1/events")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_events_with_data(self, seeded_client):
        resp = seeded_client.get("/api/v1/events")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_filter_by_country(self, seeded_client):
        resp = seeded_client.get("/api/v1/events?country=Brazil")
        data = resp.json()
        assert all("Brazil" in item["country"] for item in data["items"])

    def test_filter_by_alert_level(self, seeded_client):
        resp = seeded_client.get("/api/v1/events?alert_level=SYSTEMIC")
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == "evt-002"

    def test_filter_by_min_ci(self, seeded_client):
        resp = seeded_client.get("/api/v1/events?min_ci=3")
        data = resp.json()
        assert all(len(item["networks"]) >= 3 for item in data["items"])

    def test_get_event_detail(self, seeded_client):
        resp = seeded_client.get("/api/v1/events/evt-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "evt-001"
        assert data["country"] == "Brazil"
        assert len(data["threshold_crossings"]) == 1

    def test_get_event_not_found(self, seeded_client):
        resp = seeded_client.get("/api/v1/events/nonexistent")
        assert resp.status_code == 404


# --- Threshold endpoints ---


class TestThresholdEndpoints:
    def test_list_thresholds(self, db_and_client):
        _, client = db_and_client
        resp = client.get("/api/v1/thresholds")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 25

    def test_threshold_status(self, seeded_client):
        resp = seeded_client.get("/api/v1/thresholds/status")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["status"] == "EXCEEDED"


# --- Convergence endpoints ---


class TestConvergenceEndpoints:
    def test_list_convergence_scores(self, seeded_client):
        resp = seeded_client.get("/api/v1/convergence")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_convergence_matrix(self, seeded_client):
        resp = seeded_client.get("/api/v1/convergence/matrix")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["labels"]) == 8
        assert len(data["matrix"]) == 8
        assert len(data["matrix"][0]) == 8


# --- Network endpoints ---


class TestNetworkEndpoints:
    def test_list_networks(self, seeded_client):
        resp = seeded_client.get("/api/v1/networks")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8
        carbon = next(n for n in data if n["roman"] == "I")
        assert carbon["event_count"] >= 1

    def test_get_network_detail(self, seeded_client):
        resp = seeded_client.get("/api/v1/networks/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["roman"] == "I"
        assert "layers" in data

    def test_get_network_not_found(self, seeded_client):
        resp = seeded_client.get("/api/v1/networks/99")
        assert resp.status_code == 404


# --- Pipeline endpoints ---


class TestPipelineEndpoints:
    def test_pipeline_status_no_runs(self, db_and_client):
        _, client = db_and_client
        resp = client.get("/api/v1/pipeline/status")
        assert resp.status_code == 200
        assert resp.json()["status"] == "no_runs"

    def test_pipeline_status_with_run(self, seeded_client):
        resp = seeded_client.get("/api/v1/pipeline/status")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_pipeline_history(self, seeded_client):
        resp = seeded_client.get("/api/v1/pipeline/history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1


# --- Report endpoints ---


class TestReportEndpoints:
    def test_list_reports_empty(self, db_and_client):
        _, client = db_and_client
        resp = client.get("/api/v1/reports")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_generate_briefing(self, seeded_client):
        resp = seeded_client.post(
            "/api/v1/reports/briefing",
            json={"since": "2026-01-01", "until": "2026-02-10"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "filename" in data
        assert data["filename"].startswith("briefing_")

    def test_generate_flash_alert_requires_event(self, seeded_client):
        resp = seeded_client.post("/api/v1/reports/flash-alert", json={})
        assert resp.status_code == 400

    def test_generate_flash_alert(self, seeded_client):
        resp = seeded_client.post(
            "/api/v1/reports/flash-alert", json={"event_id": "evt-001"}
        )
        assert resp.status_code == 200
        assert resp.json()["filename"].startswith("flash_")

    def test_reports_listed_after_generation(self, seeded_client):
        seeded_client.post(
            "/api/v1/reports/briefing",
            json={"since": "2026-01-01", "until": "2026-02-10"},
        )
        resp = seeded_client.get("/api/v1/reports")
        assert len(resp.json()) >= 1
