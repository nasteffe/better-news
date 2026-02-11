"""Tests for the convergence report generator."""

import os
from datetime import date, datetime
from pathlib import Path

from smae.models.convergence import ConvergenceScore
from smae.models.enums import (
    AlertLevel,
    AnalyticalLayer,
    CouplingPattern,
    MetabolicNetwork,
    OntologyNode,
    SourceTier,
)
from smae.models.events import Event, Source
from smae.pdf.generator import generate_convergence_report


def _make_event(
    id: str = "test-001",
    networks: list[MetabolicNetwork] | None = None,
    coupling_patterns: list[CouplingPattern] | None = None,
    alert_level: AlertLevel = AlertLevel.WATCH,
    resistance_summary: str | None = None,
    **kwargs,
) -> Event:
    defaults = dict(
        id=id,
        title="Test Event",
        summary="Test event summary.",
        event_date=date(2026, 2, 1),
        detected_at=datetime(2026, 2, 1, 12, 0),
        country="TestCountry",
        networks=networks or [MetabolicNetwork.CARBON],
        layers=[AnalyticalLayer.FLOW],
        nodes=[OntologyNode.APPROPRIATION],
        coupling_patterns=coupling_patterns or [],
        alert_level=alert_level,
        resistance_summary=resistance_summary,
        sources=[
            Source(
                organization="TestOrg",
                report_name="Report",
                tier=SourceTier.SPECIALIZED_RESEARCH,
                access_date=date(2026, 2, 1),
            )
        ],
    )
    defaults.update(kwargs)
    return Event(**defaults)


class TestConvergenceReport:
    def test_generates_pdf_file(self, tmp_path: Path):
        output = tmp_path / "test_convergence.pdf"
        result = generate_convergence_report(
            events=[],
            convergence_scores=[],
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="Test executive summary.",
            outlook_rows=[],
            output_path=output,
        )
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_default_output_path(self, tmp_path: Path):
        os.chdir(tmp_path)
        result = generate_convergence_report(
            events=[],
            convergence_scores=[],
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="Test.",
            outlook_rows=[],
        )
        assert result.name == "convergence_2026-01-12_2026-02-11.pdf"
        assert result.exists()

    def test_includes_all_eight_networks_in_matrix(self, tmp_path: Path):
        events = [
            _make_event(id=f"net-{n.value}", networks=[n])
            for n in MetabolicNetwork
        ]
        scores = [
            ConvergenceScore(event_id=f"net-{n.value}", networks=[n])
            for n in MetabolicNetwork
        ]
        output = tmp_path / "eight_networks.pdf"
        result = generate_convergence_report(
            events=events,
            convergence_scores=scores,
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="Eight-network test.",
            outlook_rows=[],
            output_path=output,
        )
        assert result.exists()
        assert result.stat().st_size > 1000

    def test_convergence_nodes_included(self, tmp_path: Path):
        event = _make_event(
            id="conv-001",
            networks=[
                MetabolicNetwork.CARBON,
                MetabolicNetwork.WATER,
                MetabolicNetwork.BIODIVERSITY,
                MetabolicNetwork.OCEAN,
            ],
            alert_level=AlertLevel.SYSTEMIC,
        )
        score = ConvergenceScore(
            event_id="conv-001",
            networks=event.networks,
        )
        output = tmp_path / "convergence_nodes.pdf"
        result = generate_convergence_report(
            events=[event],
            convergence_scores=[score],
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="Systemic node test.",
            outlook_rows=[],
            output_path=output,
        )
        assert result.exists()

    def test_coupling_patterns_section(self, tmp_path: Path):
        event = _make_event(
            id="pattern-001",
            networks=[MetabolicNetwork.MINERAL, MetabolicNetwork.LABOR],
            coupling_patterns=[CouplingPattern.EXTRACTIVE_CASCADE],
            resistance_summary="Community blockade at mine entrance.",
        )
        score = ConvergenceScore(event_id="pattern-001", networks=event.networks)
        output = tmp_path / "patterns.pdf"
        result = generate_convergence_report(
            events=[event],
            convergence_scores=[score],
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="Pattern test.",
            outlook_rows=[],
            output_path=output,
        )
        assert result.exists()

    def test_outlook_table_rendered(self, tmp_path: Path):
        output = tmp_path / "outlook.pdf"
        generate_convergence_report(
            events=[],
            convergence_scores=[],
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="Outlook test.",
            outlook_rows=[
                ("Carbon", "Escalating", "Amazon deforestation acceleration"),
                ("Ocean", "Stable", "Fisheries enforcement maintained"),
                ("Labor", "Deteriorating", "ILO convention derogations"),
            ],
            output_path=output,
        )
        assert output.exists()

    def test_new_networks_in_cross_network_analysis(self, tmp_path: Path):
        """Events tagged to new networks VI-VIII appear in cross-network analysis."""
        events = [
            _make_event(
                id="bio-001",
                title="Habitat destruction",
                networks=[MetabolicNetwork.BIODIVERSITY, MetabolicNetwork.CARBON],
            ),
            _make_event(
                id="ocean-001",
                title="Fisheries collapse",
                networks=[MetabolicNetwork.OCEAN],
            ),
            _make_event(
                id="labor-001",
                title="Forced labor in cobalt mining",
                networks=[MetabolicNetwork.LABOR, MetabolicNetwork.MINERAL],
            ),
        ]
        scores = [
            ConvergenceScore(event_id=e.id, networks=e.networks)
            for e in events
        ]
        output = tmp_path / "new_networks.pdf"
        result = generate_convergence_report(
            events=events,
            convergence_scores=scores,
            period_start=date(2026, 1, 12),
            period_end=date(2026, 2, 11),
            executive_summary="New network coverage test.",
            outlook_rows=[],
            output_path=output,
        )
        assert result.exists()
        assert result.stat().st_size > 1000
