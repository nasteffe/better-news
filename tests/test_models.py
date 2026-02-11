"""Tests for SMAE core data models."""

from datetime import date, datetime

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
from smae.models.convergence import ConvergenceScore


def _make_event(**overrides) -> Event:
    """Helper to create a test event with sensible defaults."""
    defaults = dict(
        id="test-001",
        title="Test Event",
        summary="A test event for unit testing.",
        event_date=date(2026, 2, 11),
        detected_at=datetime(2026, 2, 11, 12, 0),
        country="TestCountry",
        networks=[MetabolicNetwork.CARBON],
        layers=[AnalyticalLayer.FLOW],
        nodes=[OntologyNode.APPROPRIATION],
    )
    defaults.update(overrides)
    return Event(**defaults)


class TestMetabolicNetwork:
    def test_network_labels(self):
        assert MetabolicNetwork.CARBON.label == "Carbon Accumulation"
        assert MetabolicNetwork.WATER.label == "Water Appropriation"
        assert MetabolicNetwork.SOIL.label == "Soil Fertility Transfer"
        assert MetabolicNetwork.MINERAL.label == "Mineral Extraction"
        assert MetabolicNetwork.ATMOSPHERIC.label == "Atmospheric Commons Degradation"

    def test_roman_numerals(self):
        assert MetabolicNetwork.CARBON.roman == "I"
        assert MetabolicNetwork.WATER.roman == "II"
        assert MetabolicNetwork.SOIL.roman == "III"
        assert MetabolicNetwork.MINERAL.roman == "IV"
        assert MetabolicNetwork.ATMOSPHERIC.roman == "V"

    def test_all_five_networks(self):
        assert len(MetabolicNetwork) == 5


class TestCouplingPattern:
    def test_all_eleven_patterns(self):
        assert len(CouplingPattern) == 11

    def test_pattern_labels(self):
        assert CouplingPattern.EXTRACTIVE_CASCADE.label == "Extractive Cascade"
        assert CouplingPattern.GREEN_TRANSITION_PARADOX.label == "Green Transition Paradox"
        assert CouplingPattern.INFRASTRUCTURE_LOCKIN.label == "Infrastructure Lock-in Ratchet"


class TestEvent:
    def test_convergence_index_single(self):
        event = _make_event(networks=[MetabolicNetwork.CARBON])
        assert event.convergence_index == 1
        assert not event.is_convergence_node

    def test_convergence_index_multi(self):
        event = _make_event(
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.WATER, MetabolicNetwork.MINERAL]
        )
        assert event.convergence_index == 3
        assert event.is_convergence_node

    def test_convergence_index_deduplicates(self):
        event = _make_event(
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.CARBON, MetabolicNetwork.WATER]
        )
        assert event.convergence_index == 2

    def test_network_labels_string(self):
        event = _make_event(
            networks=[MetabolicNetwork.MINERAL, MetabolicNetwork.CARBON]
        )
        assert "I: Carbon Accumulation" in event.network_labels
        assert "IV: Mineral Extraction" in event.network_labels


class TestThresholdMetric:
    def test_comparison_string_exceeded(self):
        metric = ThresholdMetric(
            name="displacement_single_event",
            category=ThresholdCategory.ABSOLUTE,
            networks=[MetabolicNetwork.CARBON],
            baseline_value=50_000,
            baseline_date=date(2025, 12, 1),
            delta=70_000,
            current_value=120_000,
            threshold_value=100_000,
            unit="persons",
            status=ThresholdStatus.EXCEEDED,
        )
        result = metric.comparison_string
        assert "[EXCEEDED]" in result
        assert "persons" in result

    def test_comparison_string_below(self):
        metric = ThresholdMetric(
            name="test_metric",
            category=ThresholdCategory.ABSOLUTE,
            networks=[MetabolicNetwork.WATER],
            baseline_value=10_000,
            baseline_date=date(2025, 12, 1),
            delta=5_000,
            current_value=15_000,
            threshold_value=50_000,
            unit="persons",
            status=ThresholdStatus.BELOW,
        )
        result = metric.comparison_string
        assert "[EXCEEDED]" not in result


class TestConvergenceScore:
    def test_single_network(self):
        cs = ConvergenceScore(
            event_id="test-001",
            networks=[MetabolicNetwork.CARBON],
        )
        assert cs.ci_score == 1.0
        assert cs.classification == "Single-network"
        assert cs.recommended_alert_level == AlertLevel.MONITOR

    def test_multi_network(self):
        cs = ConvergenceScore(
            event_id="test-002",
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.WATER],
        )
        assert cs.ci_score == 2.0
        assert cs.classification == "Multi-network"
        assert cs.recommended_alert_level == AlertLevel.ALERT

    def test_systemic_node(self):
        cs = ConvergenceScore(
            event_id="test-003",
            networks=[
                MetabolicNetwork.CARBON,
                MetabolicNetwork.WATER,
                MetabolicNetwork.SOIL,
                MetabolicNetwork.MINERAL,
            ],
        )
        assert cs.ci_score == 4.0
        assert cs.classification == "Systemic node"
        assert cs.recommended_alert_level == AlertLevel.SYSTEMIC

    def test_weighted_scoring(self):
        cs = ConvergenceScore(
            event_id="test-004",
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.WATER],
            severity_weights={
                MetabolicNetwork.CARBON: 2.5,
                MetabolicNetwork.WATER: 1.5,
            },
        )
        assert cs.ci_score == 4.0
        assert cs.classification == "Systemic node"


class TestSource:
    def test_citation_with_doi(self):
        src = Source(
            organization="IPCC",
            report_name="AR6 WGIII",
            doi="10.1017/9781009157926",
            tier=SourceTier.ACADEMIC_PEER_REVIEWED,
            access_date=date(2026, 2, 11),
        )
        assert "IPCC" in src.citation
        assert "10.1017" in src.citation

    def test_citation_without_doi(self):
        src = Source(
            organization="ACLED",
            report_name="Weekly Update",
            tier=SourceTier.SPECIALIZED_RESEARCH,
            access_date=date(2026, 2, 11),
        )
        assert "ACLED" in src.citation
        assert "Weekly Update" in src.citation

    def test_provisional_flag(self):
        src = Source(
            organization="Test",
            report_name="Test Report",
            tier=SourceTier.GOVERNMENT_REGULATORY,
            access_date=date(2026, 2, 11),
            provisional=True,
        )
        assert src.provisional is True
