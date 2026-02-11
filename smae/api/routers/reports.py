"""Report endpoints — generate and download PDF reports."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from smae.api.deps import get_db
from smae.api.models import GenerateReportRequest, ReportResponse

REPORTS_DIR = Path("reports")

router = APIRouter(tags=["reports"])


def _ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    return REPORTS_DIR


@router.post("/reports/briefing")
async def generate_briefing(req: GenerateReportRequest) -> dict:
    from smae.pdf.generator import generate_daily_briefing

    db = get_db()
    briefing_date = req.until or date.today()
    since = req.since or (briefing_date - timedelta(days=2))

    events, _ = await db.get_events(since=since, until=briefing_date, limit=500)

    output_dir = _ensure_reports_dir()
    filename = f"briefing_{briefing_date.isoformat()}.pdf"
    output_path = output_dir / filename

    generate_daily_briefing(
        events=events,
        briefing_date=briefing_date,
        executive_summary=(
            f"{len(events)} events analyzed. "
            f"{sum(len(e.threshold_crossings) for e in events)} threshold crossings."
            if events
            else "No events in the requested period."
        ),
        outlook_rows=[],
        output_path=output_path,
    )

    report_id = await db.store_report("briefing", filename, str(output_path))
    return {"report_id": report_id, "filename": filename}


@router.post("/reports/flash-alert")
async def generate_flash_alert(req: GenerateReportRequest) -> dict:
    from smae.pdf.generator import generate_flash_alert

    if not req.event_id:
        raise HTTPException(status_code=400, detail="event_id is required")

    db = get_db()
    event = await db.get_event(req.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    output_dir = _ensure_reports_dir()
    filename = f"flash_{event.event_date.isoformat()}_{event.id}.pdf"
    output_path = output_dir / filename

    generate_flash_alert(event=event, output_path=output_path)

    report_id = await db.store_report("flash_alert", filename, str(output_path))
    return {"report_id": report_id, "filename": filename}


@router.post("/reports/convergence")
async def generate_convergence(req: GenerateReportRequest) -> dict:
    from smae.pdf.generator import generate_convergence_report

    db = get_db()
    period_end = req.until or date.today()
    period_start = req.since or (period_end - timedelta(days=30))

    events, _ = await db.get_events(since=period_start, until=period_end, limit=1000)
    scores = await db.get_convergence_scores()

    output_dir = _ensure_reports_dir()
    filename = f"convergence_{period_start.isoformat()}_{period_end.isoformat()}.pdf"
    output_path = output_dir / filename

    generate_convergence_report(
        events=events,
        convergence_scores=scores,
        period_start=period_start,
        period_end=period_end,
        executive_summary=(
            f"{len(events)} events analyzed over "
            f"{(period_end - period_start).days}-day period."
            if events
            else "No events in the requested period."
        ),
        outlook_rows=[],
        output_path=output_path,
    )

    report_id = await db.store_report("convergence", filename, str(output_path))
    return {"report_id": report_id, "filename": filename}


@router.get("/reports", response_model=list[ReportResponse])
async def list_reports() -> list[ReportResponse]:
    db = get_db()
    reports = await db.get_reports()
    return [ReportResponse(**r) for r in reports]


@router.get("/reports/download/{filename}")
async def download_report(filename: str) -> FileResponse:
    path = REPORTS_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)
