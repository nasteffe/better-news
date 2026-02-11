"""Convergence analysis models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from smae.models.enums import AlertLevel, MetabolicNetwork


class ConvergenceScore(BaseModel):
    """Multi-network convergence scoring for an event or event cluster.

    CI = Sum(network involvement x severity weight)
    CI 1   -> Single-network, monitor per network thresholds
    CI 2-3 -> Multi-network, escalate to cross-network analysis
    CI >= 4 -> Systemic node, immediate high-priority briefing
    """

    event_id: str
    networks: list[MetabolicNetwork]
    severity_weights: dict[MetabolicNetwork, float] = Field(default_factory=dict)

    @property
    def ci_score(self) -> float:
        if not self.severity_weights:
            return float(len(set(self.networks)))
        return sum(self.severity_weights.get(n, 1.0) for n in set(self.networks))

    @property
    def classification(self) -> str:
        score = self.ci_score
        if score >= 4:
            return "Systemic node"
        elif score >= 2:
            return "Multi-network"
        return "Single-network"

    @property
    def recommended_action(self) -> str:
        score = self.ci_score
        if score >= 4:
            return "Immediate high-priority briefing, structural analysis"
        elif score >= 2:
            return "Escalate to cross-network analysis"
        return "Monitor per network thresholds"

    @property
    def recommended_alert_level(self) -> AlertLevel:
        score = self.ci_score
        if score >= 4:
            return AlertLevel.SYSTEMIC
        elif score >= 3:
            return AlertLevel.CRITICAL
        elif score >= 2:
            return AlertLevel.ALERT
        return AlertLevel.MONITOR
