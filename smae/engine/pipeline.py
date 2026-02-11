"""SMAE analytical workflow pipeline.

Implements the seven-stage daily analytical cycle:
    0. INTAKE   — Scan source feeds across all five priority tiers
    1. TAG      — Assign network(s) and layer(s) to incoming events
    2. THRESHOLD — Evaluate all active metrics; flag crossings/near-crossings
    3. CONVERGE — Score for multi-network involvement; identify CI>=2 nodes
    4. RESISTANCE — Identify contestation; link to contested flows
    5. TRIAGE   — Assign alert levels
    6. PRODUCE  — Generate appropriate output product
    7. VERIFY   — Triangulate per source protocol; mark provisional
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol, Sequence

from smae.models.convergence import ConvergenceScore
from smae.models.enums import AlertLevel, MetabolicNetwork, ThresholdStatus
from smae.models.events import Event, ThresholdCrossing, ThresholdMetric
from smae.models.thresholds import ALL_THRESHOLDS, ThresholdDefinition


class DataSource(Protocol):
    """Protocol for data source adapters."""

    async def fetch_events(self, since: date) -> list[Event]: ...


@dataclass
class PipelineResult:
    """Output of a complete pipeline run."""

    run_date: date
    events: list[Event] = field(default_factory=list)
    threshold_crossings: list[ThresholdCrossing] = field(default_factory=list)
    convergence_nodes: list[ConvergenceScore] = field(default_factory=list)
    alert_events: list[Event] = field(default_factory=list)
    executive_summary: str = ""


class AnalyticalPipeline:
    """The SMAE seven-stage analytical workflow."""

    def __init__(self, sources: Sequence[DataSource] | None = None):
        self._sources: list[DataSource] = list(sources) if sources else []
        self._threshold_defs: list[ThresholdDefinition] = ALL_THRESHOLDS

    def register_source(self, source: DataSource) -> None:
        self._sources.append(source)

    # --- Stage 0: INTAKE ---

    async def intake(self, since: date) -> list[Event]:
        """Scan all registered source feeds for events since given date."""
        all_events: list[Event] = []
        for source in self._sources:
            events = await source.fetch_events(since)
            all_events.extend(events)
        return all_events

    # --- Stage 1: TAG ---

    @staticmethod
    def tag(events: list[Event]) -> list[Event]:
        """Ensure all events have network and layer assignments.

        Events arriving from sources should already be tagged. This stage
        validates completeness and applies any additional tagging rules.
        """
        for event in events:
            if not event.networks:
                raise ValueError(f"Event {event.id} has no network assignment")
            if not event.layers:
                raise ValueError(f"Event {event.id} has no layer assignment")
        return events

    # --- Stage 2: THRESHOLD ---

    @staticmethod
    def evaluate_thresholds(events: list[Event]) -> list[Event]:
        """Evaluate threshold crossings for all events.

        Events may arrive with pre-computed threshold crossings from sources,
        or crossings can be detected here based on metric values.
        """
        for event in events:
            for tc in event.threshold_crossings:
                m = tc.metric
                if m.current_value > m.threshold_value:
                    m.status = ThresholdStatus.EXCEEDED
                elif m.current_value > m.threshold_value * 0.8:
                    m.status = ThresholdStatus.APPROACHING
                else:
                    m.status = ThresholdStatus.BELOW
        return events

    # --- Stage 3: CONVERGE ---

    @staticmethod
    def score_convergence(events: list[Event]) -> list[ConvergenceScore]:
        """Score all events for multi-network convergence."""
        scores = []
        for event in events:
            score = ConvergenceScore(
                event_id=event.id,
                networks=event.networks,
            )
            scores.append(score)
        return scores

    # --- Stage 4: RESISTANCE ---

    @staticmethod
    def link_resistance(events: list[Event]) -> list[Event]:
        """Ensure resistance data is present and linked to contested flows.

        Resistance is primary evidence, not afterthought. Flag events
        missing resistance context for follow-up.
        """
        for event in events:
            if not event.resistance_summary:
                event.resistance_summary = (
                    "[PENDING] Resistance data not yet collected for this event. "
                    "Requires follow-up from frontline/EJ sources."
                )
        return events

    # --- Stage 5: TRIAGE ---

    @staticmethod
    def triage(events: list[Event], convergence_scores: list[ConvergenceScore]) -> list[Event]:
        """Assign alert levels based on threshold crossings and convergence."""
        score_map = {cs.event_id: cs for cs in convergence_scores}

        for event in events:
            cs = score_map.get(event.id)
            has_exceeded = any(
                tc.metric.status == ThresholdStatus.EXCEEDED
                for tc in event.threshold_crossings
            )
            has_approaching = any(
                tc.metric.status == ThresholdStatus.APPROACHING
                for tc in event.threshold_crossings
            )

            if cs and cs.ci_score >= 4 and has_exceeded:
                event.alert_level = AlertLevel.SYSTEMIC
            elif cs and cs.ci_score >= 3 and has_exceeded:
                event.alert_level = AlertLevel.CRITICAL
            elif has_exceeded:
                event.alert_level = AlertLevel.ALERT
            elif has_approaching or (cs and cs.ci_score >= 2):
                event.alert_level = AlertLevel.MONITOR
            else:
                event.alert_level = AlertLevel.WATCH

        return events

    # --- Stage 6: PRODUCE ---
    # Delegated to smae.pdf.generator — the pipeline prepares the data,
    # the generator builds the output product.

    # --- Stage 7: VERIFY ---

    @staticmethod
    def verify(events: list[Event]) -> list[Event]:
        """Apply triangulation protocol and mark provisional data.

        Flags events that don't meet the source triangulation requirements:
        - Quantitative claims: >=2 independent sources
        - Event claims: >=2 sources from different hierarchy categories
        - Attribution claims: >=3 independent sources
        """
        for event in events:
            source_tiers = {s.tier for s in event.sources}
            if len(event.sources) < 2:
                for src in event.sources:
                    src.provisional = True
            elif len(source_tiers) < 2:
                # All sources from same tier — mark provisional
                for src in event.sources:
                    src.provisional = True
            # Actor attribution requires 3 sources
            if event.actors and len(event.sources) < 3:
                for src in event.sources:
                    src.provisional = True
        return events

    # --- Full pipeline run ---

    async def run(self, since: date) -> PipelineResult:
        """Execute the complete seven-stage analytical workflow."""
        result = PipelineResult(run_date=date.today())

        # 0. Intake
        events = await self.intake(since)

        # 1. Tag
        events = self.tag(events)

        # 2. Threshold
        events = self.evaluate_thresholds(events)

        # 3. Converge
        convergence_scores = self.score_convergence(events)

        # 4. Resistance
        events = self.link_resistance(events)

        # 5. Triage
        events = self.triage(events, convergence_scores)

        # 7. Verify (before produce, so provisional flags are set)
        events = self.verify(events)

        result.events = events
        result.convergence_nodes = [
            cs for cs in convergence_scores if cs.ci_score >= 2
        ]
        result.threshold_crossings = [
            tc for event in events for tc in event.threshold_crossings
            if tc.metric.status == ThresholdStatus.EXCEEDED
        ]
        result.alert_events = [
            e for e in events
            if e.alert_level in (AlertLevel.ALERT, AlertLevel.CRITICAL, AlertLevel.SYSTEMIC)
        ]

        return result
