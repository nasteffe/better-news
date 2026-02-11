"""Pipeline endpoints — trigger runs and check status."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import date, timedelta

from fastapi import APIRouter, BackgroundTasks

from smae.api.deps import get_db
from smae.api.models import PipelineRunResponse

router = APIRouter(tags=["pipeline"])


async def _run_pipeline(run_id: str, since: date) -> None:
    """Execute the analytical pipeline in the background."""
    from smae.engine.pipeline import AnalyticalPipeline
    from smae.sources.acled import ACLEDAdapter
    from smae.sources.gfw import GFWAdapter
    from smae.sources.idmc import IDMCAdapter

    db = get_db()
    sources = []

    acled_email = os.environ.get("SMAE_ACLED_EMAIL")
    acled_password = os.environ.get("SMAE_ACLED_PASSWORD")
    if acled_email and acled_password:
        sources.append(ACLEDAdapter(credentials={"email": acled_email, "password": acled_password}))
    sources.append(GFWAdapter(api_key=os.environ.get("SMAE_GFW_KEY")))
    sources.append(IDMCAdapter(api_key=os.environ.get("SMAE_IDMC_KEY")))

    pipeline = AnalyticalPipeline(sources=sources)

    try:
        result = await pipeline.run(since)

        await db.store_events(run_id, result.events)
        await db.store_convergence_scores(run_id, result.convergence_nodes)
        await db.finish_pipeline_run(
            run_id,
            status="completed",
            events_ingested=len(result.events),
            threshold_crossings=len(result.threshold_crossings),
            convergence_nodes=len(result.convergence_nodes),
        )
    except Exception as exc:
        await db.finish_pipeline_run(
            run_id, status="failed", source_errors=[str(exc)]
        )
    finally:
        for src in sources:
            await src.close()


@router.post("/pipeline/run")
async def trigger_pipeline_run(
    background_tasks: BackgroundTasks,
    lookback_days: int = 2,
) -> dict:
    db = get_db()
    run_id = await db.start_pipeline_run()
    since = date.today() - timedelta(days=lookback_days)
    background_tasks.add_task(_run_pipeline, run_id, since)
    return {"run_id": run_id, "status": "started", "since": since.isoformat()}


@router.get("/pipeline/status")
async def pipeline_status() -> dict:
    db = get_db()
    run = await db.get_latest_run()
    if run is None:
        return {"status": "no_runs", "message": "No pipeline runs recorded"}
    run["source_errors"] = json.loads(run.get("source_errors", "[]"))
    return run


@router.get("/pipeline/history", response_model=list[PipelineRunResponse])
async def pipeline_history(limit: int = 20) -> list[PipelineRunResponse]:
    db = get_db()
    runs = await db.get_pipeline_runs(limit=limit)
    result = []
    for r in runs:
        r["source_errors"] = json.loads(r.get("source_errors", "[]"))
        result.append(PipelineRunResponse(**r))
    return result
