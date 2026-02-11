"""API-specific response models.

Wraps existing SMAE Pydantic models with pagination and summary types
needed by the dashboard endpoints.
"""

from __future__ import annotations

from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel

from smae.models.enums import AlertLevel, MetabolicNetwork

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class NetworkSummary(BaseModel):
    network_id: int
    roman: str
    label: str
    event_count: int
    convergent_count: int
    threshold_crossings: int
    max_alert: str


class ConvergenceMatrixResponse(BaseModel):
    """Network-to-network co-occurrence counts."""

    labels: list[str]
    matrix: list[list[int]]


class PipelineRunResponse(BaseModel):
    id: str
    run_date: str
    started_at: str
    finished_at: str | None = None
    status: str
    events_ingested: int
    threshold_crossings: int
    convergence_nodes: int
    source_errors: list[str]


class ThresholdDefinitionResponse(BaseModel):
    name: str
    category: str
    description: str
    networks: list[int]
    threshold_value: float
    unit: str


class ReportResponse(BaseModel):
    id: str
    created_at: str
    report_type: str
    filename: str


class GenerateReportRequest(BaseModel):
    """Request body for report generation endpoints."""

    since: date | None = None
    until: date | None = None
    event_id: str | None = None
