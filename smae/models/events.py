"""Event and threshold models for the SMAE analytical framework."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

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


class Source(BaseModel):
    """A source reference following the SMAE source hierarchy."""

    organization: str
    report_name: str
    doi: Optional[str] = None
    report_id: Optional[str] = None
    tier: SourceTier
    access_date: date
    provisional: bool = False

    @property
    def citation(self) -> str:
        parts = [self.organization, self.report_name]
        if self.doi:
            parts.append(self.doi)
        elif self.report_id:
            parts.append(self.report_id)
        return " — ".join(parts)


class Actor(BaseModel):
    """An actor involved in appropriation, governance, or resistance."""

    name: str
    actor_type: str  # e.g., "corporation", "state", "armed_group", "community", "NGO"
    jurisdiction: Optional[str] = None
    role: str  # e.g., "extractor", "enabler", "beneficiary", "resister"


class ThresholdMetric(BaseModel):
    """A single threshold metric with baseline-delta-current-threshold comparison."""

    name: str
    category: ThresholdCategory
    networks: list[MetabolicNetwork]
    baseline_value: float
    baseline_date: date
    delta: float
    current_value: float
    threshold_value: float
    unit: str
    status: ThresholdStatus

    @property
    def comparison_string(self) -> str:
        """Format: Baseline value (date) + Delta = Current <= Threshold [STATUS]."""
        status_tag = f" [{self.status.value}]" if self.status == ThresholdStatus.EXCEEDED else ""
        return (
            f"{self.baseline_value:,.1f} {self.unit} ({self.baseline_date.isoformat()}) "
            f"+ {self.delta:+,.1f} = {self.current_value:,.1f} "
            f"<= {self.threshold_value:,.1f}{status_tag}"
        )


class ThresholdCrossing(BaseModel):
    """A detected threshold crossing event."""

    metric: ThresholdMetric
    detected_at: datetime
    alert_level: AlertLevel
    notes: str = ""


class Event(BaseModel):
    """A tagged analytical event decomposed through the SMAE ontology.

    Every event is tagged to network(s), layer(s), ontology node(s), and
    optionally linked to structural coupling patterns.
    """

    id: str = Field(description="Unique event identifier")
    title: str
    summary: str
    event_date: date
    detected_at: datetime

    # Geographic
    country: str
    region: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = None

    # Ontological tagging
    networks: list[MetabolicNetwork]
    layers: list[AnalyticalLayer]
    nodes: list[OntologyNode]
    coupling_patterns: list[CouplingPattern] = Field(default_factory=list)

    # Actors
    actors: list[Actor] = Field(default_factory=list)

    # Thresholds
    threshold_crossings: list[ThresholdCrossing] = Field(default_factory=list)

    # Sources
    sources: list[Source] = Field(default_factory=list)

    # Triage
    alert_level: AlertLevel = AlertLevel.WATCH

    # Resistance data (always included, never afterthought)
    resistance_summary: Optional[str] = None

    # Governance context
    governance_context: Optional[str] = None

    # Outlook
    outlook_30d: Optional[str] = None

    @property
    def convergence_index(self) -> int:
        """CI = count of distinct networks involved."""
        return len(set(self.networks))

    @property
    def is_convergence_node(self) -> bool:
        return self.convergence_index >= 2

    @property
    def network_labels(self) -> str:
        return ", ".join(f"{n.roman}: {n.label}" for n in sorted(set(self.networks)))
