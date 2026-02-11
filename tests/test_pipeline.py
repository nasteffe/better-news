"""Tests for the SMAE analytical pipeline."""

import asyncio
from datetime import date, datetime

import pytest

from smae.engine.pipeline import AnalyticalPipeline, PipelineResult
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


def _make_event(
    id: str = "test-001",
    networks: list[MetabolicNetwork] | None = None,
    threshold_crossings: list[ThresholdCrossing] | None = None,
    sources: list[Source] | None = None,
    **kwargs,
) -> Event:
    defaults = dict(
        id=id,
        title="Test Event",
        summary="Test event summary.",
        event_date=date(2026, 2, 11),
        detected_at=datetime(2026, 2, 11, 12, 0),
        country="TestCountry",
        networks=networks or [MetabolicNetwork.CARBON],
        layers=[AnalyticalLayer.FLOW],
        nodes=[OntologyNode.APPROPRIATION],
        threshold_crossings=threshold_crossings or [],
        sources=sources or [
            Source(
                organization="TestOrg",
                report_name="Test Report",
                tier=SourceTier.SPECIALIZED_RESEARCH,
                access_date=date(2026, 2, 11),
            ),
            Source(
                organization="TestOrg2",
                report_name="Test Report 2",
                tier=SourceTier.UN_OPERATIONAL,
                access_date=date(2026, 2, 11),
            ),
        ],
    )
    defaults.update(kwargs)
    return Event(**defaults)


def _make_threshold_crossing(
    current: float = 150_000,
    threshold: float = 100_000,
    status: ThresholdStatus = ThresholdStatus.EXCEEDED,
) -> ThresholdCrossing:
    return ThresholdCrossing(
        metric=ThresholdMetric(
            name="displacement_single_event",
            category=ThresholdCategory.ABSOLUTE,
            networks=[MetabolicNetwork.CARBON],
            baseline_value=50_000,
            baseline_date=date(2025, 12, 1),
            delta=current - 50_000,
            current_value=current,
            threshold_value=threshold,
            unit="persons",
            status=status,
        ),
        detected_at=datetime(2026, 2, 11, 12, 0),
        alert_level=AlertLevel.ALERT,
    )


class TestPipelineTag:
    def test_valid_events_pass(self):
        pipeline = AnalyticalPipeline()
        events = [_make_event()]
        result = pipeline.tag(events)
        assert len(result) == 1

    def test_missing_network_raises(self):
        pipeline = AnalyticalPipeline()
        event = _make_event()
        event.networks = []
        with pytest.raises(ValueError, match="no network assignment"):
            pipeline.tag([event])

    def test_missing_layers_raises(self):
        pipeline = AnalyticalPipeline()
        event = _make_event()
        event.layers = []
        with pytest.raises(ValueError, match="no layer assignment"):
            pipeline.tag([event])


class TestPipelineThreshold:
    def test_exceeded_detection(self):
        pipeline = AnalyticalPipeline()
        tc = _make_threshold_crossing(current=150_000, threshold=100_000)
        tc.metric.status = ThresholdStatus.BELOW  # Reset so pipeline detects it
        event = _make_event(threshold_crossings=[tc])
        result = pipeline.evaluate_thresholds([event])
        assert result[0].threshold_crossings[0].metric.status == ThresholdStatus.EXCEEDED

    def test_approaching_detection(self):
        pipeline = AnalyticalPipeline()
        tc = _make_threshold_crossing(current=85_000, threshold=100_000)
        tc.metric.status = ThresholdStatus.BELOW
        event = _make_event(threshold_crossings=[tc])
        result = pipeline.evaluate_thresholds([event])
        assert result[0].threshold_crossings[0].metric.status == ThresholdStatus.APPROACHING

    def test_below_detection(self):
        pipeline = AnalyticalPipeline()
        tc = _make_threshold_crossing(current=50_000, threshold=100_000)
        tc.metric.status = ThresholdStatus.EXCEEDED
        event = _make_event(threshold_crossings=[tc])
        result = pipeline.evaluate_thresholds([event])
        assert result[0].threshold_crossings[0].metric.status == ThresholdStatus.BELOW


class TestPipelineConvergence:
    def test_single_network_score(self):
        pipeline = AnalyticalPipeline()
        events = [_make_event(networks=[MetabolicNetwork.CARBON])]
        scores = pipeline.score_convergence(events)
        assert len(scores) == 1
        assert scores[0].ci_score == 1.0

    def test_multi_network_score(self):
        pipeline = AnalyticalPipeline()
        events = [_make_event(
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.WATER, MetabolicNetwork.MINERAL]
        )]
        scores = pipeline.score_convergence(events)
        assert scores[0].ci_score == 3.0


class TestPipelineTriage:
    def test_systemic_alert(self):
        pipeline = AnalyticalPipeline()
        tc = _make_threshold_crossing()
        event = _make_event(
            networks=[
                MetabolicNetwork.CARBON,
                MetabolicNetwork.WATER,
                MetabolicNetwork.SOIL,
                MetabolicNetwork.MINERAL,
            ],
            threshold_crossings=[tc],
        )
        events = [event]
        scores = pipeline.score_convergence(events)
        result = pipeline.triage(events, scores)
        assert result[0].alert_level == AlertLevel.SYSTEMIC

    def test_critical_alert(self):
        pipeline = AnalyticalPipeline()
        tc = _make_threshold_crossing()
        event = _make_event(
            networks=[MetabolicNetwork.CARBON, MetabolicNetwork.WATER, MetabolicNetwork.MINERAL],
            threshold_crossings=[tc],
        )
        events = [event]
        scores = pipeline.score_convergence(events)
        result = pipeline.triage(events, scores)
        assert result[0].alert_level == AlertLevel.CRITICAL

    def test_watch_level_default(self):
        pipeline = AnalyticalPipeline()
        event = _make_event()
        events = [event]
        scores = pipeline.score_convergence(events)
        result = pipeline.triage(events, scores)
        assert result[0].alert_level == AlertLevel.WATCH


class TestPipelineResistance:
    def test_missing_resistance_flagged(self):
        pipeline = AnalyticalPipeline()
        event = _make_event()
        assert event.resistance_summary is None
        result = pipeline.link_resistance([event])
        assert result[0].resistance_summary is not None
        assert "[PENDING]" in result[0].resistance_summary

    def test_existing_resistance_preserved(self):
        pipeline = AnalyticalPipeline()
        event = _make_event(resistance_summary="Community blockade at mine entrance.")
        result = pipeline.link_resistance([event])
        assert result[0].resistance_summary == "Community blockade at mine entrance."


class TestPipelineVerify:
    def test_single_source_marked_provisional(self):
        pipeline = AnalyticalPipeline()
        event = _make_event(sources=[
            Source(
                organization="TestOrg",
                report_name="Report",
                tier=SourceTier.SPECIALIZED_RESEARCH,
                access_date=date(2026, 2, 11),
            ),
        ])
        result = pipeline.verify([event])
        assert all(s.provisional for s in result[0].sources)

    def test_two_sources_different_tiers_not_provisional(self):
        pipeline = AnalyticalPipeline()
        event = _make_event()  # default has 2 sources from different tiers
        result = pipeline.verify([event])
        assert not any(s.provisional for s in result[0].sources)

    def test_actor_attribution_needs_three_sources(self):
        pipeline = AnalyticalPipeline()
        from smae.models.events import Actor
        event = _make_event(
            actors=[Actor(name="MegaCorp", actor_type="corporation", role="extractor")],
        )
        # Only 2 sources — should mark provisional
        result = pipeline.verify([event])
        assert all(s.provisional for s in result[0].sources)


class _FakeSource:
    """Minimal source that satisfies the DataSource protocol."""

    name = "fake"

    def __init__(self, events: list[Event] | None = None, error: Exception | None = None):
        self._events = events or []
        self._error = error

    async def fetch_events(self, since: date) -> list[Event]:
        if self._error:
            raise self._error
        return self._events


class TestPipelineFullRun:
    def test_empty_pipeline_returns_empty_result(self):
        pipeline = AnalyticalPipeline()
        result = asyncio.run(pipeline.run(date(2026, 2, 9)))
        assert isinstance(result, PipelineResult)
        assert result.events == []
        assert result.threshold_crossings == []
        assert result.convergence_nodes == []


class TestPipelineIntake:
    """Tests for resilient, concurrent source intake."""

    def test_single_source_returns_events(self):
        events = [_make_event(id="src-001")]
        pipeline = AnalyticalPipeline(sources=[_FakeSource(events=events)])
        result = asyncio.run(pipeline.intake(date(2026, 2, 9)))
        assert len(result) == 1
        assert result[0].id == "src-001"

    def test_multiple_sources_merged(self):
        src_a = _FakeSource(events=[_make_event(id="a-001")])
        src_b = _FakeSource(events=[_make_event(id="b-001"), _make_event(id="b-002")])
        pipeline = AnalyticalPipeline(sources=[src_a, src_b])
        result = asyncio.run(pipeline.intake(date(2026, 2, 9)))
        assert len(result) == 3
        ids = {e.id for e in result}
        assert ids == {"a-001", "b-001", "b-002"}

    def test_failing_source_does_not_crash_pipeline(self):
        good = _FakeSource(events=[_make_event(id="good-001")])
        bad = _FakeSource(error=ConnectionError("network down"))
        pipeline = AnalyticalPipeline(sources=[good, bad])
        result = asyncio.run(pipeline.intake(date(2026, 2, 9)))
        assert len(result) == 1
        assert result[0].id == "good-001"
        assert len(pipeline._source_errors) == 1
        assert "fake" in pipeline._source_errors[0][0]

    def test_all_sources_fail_returns_empty(self):
        bad1 = _FakeSource(error=TimeoutError("timeout"))
        bad2 = _FakeSource(error=ValueError("bad data"))
        pipeline = AnalyticalPipeline(sources=[bad1, bad2])
        result = asyncio.run(pipeline.intake(date(2026, 2, 9)))
        assert result == []
        assert len(pipeline._source_errors) == 2

    def test_full_run_with_failing_source(self):
        good = _FakeSource(events=[_make_event(id="ok-001")])
        bad = _FakeSource(error=RuntimeError("auth failed"))
        pipeline = AnalyticalPipeline(sources=[good, bad])
        result = asyncio.run(pipeline.run(date(2026, 2, 9)))
        assert len(result.events) == 1
        assert result.events[0].id == "ok-001"
