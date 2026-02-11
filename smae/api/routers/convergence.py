"""Convergence endpoints — scores and network co-occurrence matrix."""

from __future__ import annotations

from fastapi import APIRouter

from smae.api.deps import get_db
from smae.api.models import ConvergenceMatrixResponse
from smae.models.convergence import ConvergenceScore
from smae.models.enums import MetabolicNetwork

router = APIRouter(tags=["convergence"])


@router.get("/convergence", response_model=list[ConvergenceScore])
async def list_convergence_scores() -> list[ConvergenceScore]:
    db = get_db()
    return await db.get_convergence_scores()


@router.get("/convergence/matrix", response_model=ConvergenceMatrixResponse)
async def convergence_matrix() -> ConvergenceMatrixResponse:
    """Build an 8x8 network co-occurrence matrix from stored events."""
    db = get_db()
    events, _ = await db.get_events(limit=1000)

    networks = list(MetabolicNetwork)
    n = len(networks)
    matrix = [[0] * n for _ in range(n)]

    for event in events:
        nets = sorted(set(event.networks))
        for i, a in enumerate(nets):
            for b in nets[i:]:
                ai = a.value - 1
                bi = b.value - 1
                matrix[ai][bi] += 1
                if ai != bi:
                    matrix[bi][ai] += 1

    return ConvergenceMatrixResponse(
        labels=[net.label for net in networks],
        matrix=matrix,
    )
