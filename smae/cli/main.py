"""CLI entry point for the SMAE analytical engine."""

from __future__ import annotations

import asyncio
import os
from datetime import date, timedelta
from pathlib import Path

import click
from dotenv import load_dotenv

from smae import __version__

load_dotenv()


@click.group()
@click.version_option(version=__version__, prog_name="smae")
def cli() -> None:
    """Socio-Metabolic Analytical Engine (SMAE).

    Tracking global resource appropriation, cost displacement,
    and frontline resistance across eight metabolic networks.
    """


@cli.command()
@click.option(
    "--date", "briefing_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Briefing date (YYYY-MM-DD). Defaults to today.",
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output PDF path. Defaults to briefing_YYYY-MM-DD.pdf.",
)
@click.option(
    "--lookback", "-l",
    type=int,
    default=2,
    help="Days to look back for events (default: 2).",
)
def briefing(
    briefing_date: date | None,
    output: Path | None,
    lookback: int,
) -> None:
    """Generate a daily briefing PDF."""
    if briefing_date is None:
        briefing_date = date.today()
    else:
        briefing_date = briefing_date.date()

    since = briefing_date - timedelta(days=lookback)

    if output is None:
        output = Path(f"briefing_{briefing_date.isoformat()}.pdf")

    click.echo(f"SMAE Daily Briefing — {briefing_date.isoformat()}")
    click.echo(f"Scanning events since {since.isoformat()}...")

    asyncio.run(_run_briefing(briefing_date, since, output))


def _build_sources() -> list:
    """Instantiate source adapters from environment variables."""
    from smae.sources.acled import ACLEDAdapter
    from smae.sources.gfw import GFWAdapter
    from smae.sources.idmc import IDMCAdapter

    sources = []

    acled_email = os.environ.get("SMAE_ACLED_EMAIL")
    acled_password = os.environ.get("SMAE_ACLED_PASSWORD")
    if acled_email and acled_password:
        sources.append(ACLEDAdapter(
            credentials={"email": acled_email, "password": acled_password},
        ))
        click.echo("  [+] ACLED adapter configured")

    gfw_key = os.environ.get("SMAE_GFW_KEY")
    if gfw_key:
        sources.append(GFWAdapter(api_key=gfw_key))
        click.echo("  [+] GFW adapter configured")
    else:
        sources.append(GFWAdapter())
        click.echo("  [~] GFW adapter configured (no API key — may be rate-limited)")

    idmc_key = os.environ.get("SMAE_IDMC_KEY")
    sources.append(IDMCAdapter(api_key=idmc_key))
    click.echo(f"  [+] IDMC adapter configured{'' if idmc_key else ' (no API key)'}")

    return sources


async def _run_briefing(briefing_date: date, since: date, output: Path) -> None:
    """Run the analytical pipeline and generate a briefing PDF."""
    from smae.engine.pipeline import AnalyticalPipeline
    from smae.pdf.generator import generate_daily_briefing

    sources = _build_sources()
    pipeline = AnalyticalPipeline(sources=sources)

    try:
        result = await pipeline.run(since)
    finally:
        for src in sources:
            await src.close()

    if not result.events:
        click.echo(
            "\nNo events returned from configured sources. "
            "Check credentials and network connectivity."
        )
        click.echo("Generating empty briefing template...")
    else:
        click.echo(
            f"\n{len(result.events)} events ingested, "
            f"{len(result.alert_events)} at ALERT level or above, "
            f"{len(result.convergence_nodes)} convergence nodes."
        )

    generate_daily_briefing(
        events=result.events,
        briefing_date=briefing_date,
        executive_summary=(
            "No events ingested. Check data source credentials and connectivity."
            if not result.events
            else f"{len(result.events)} events analyzed across "
            f"{len(set(n for e in result.events for n in e.networks))} metabolic networks. "
            f"{len(result.threshold_crossings)} threshold crossings detected. "
            f"{len(result.convergence_nodes)} convergence nodes identified."
        ),
        outlook_rows=[],
        output_path=output,
    )
    click.echo(f"Briefing written to {output}")


@cli.command()
@click.option(
    "--end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="End of reporting period (YYYY-MM-DD). Defaults to today.",
)
@click.option(
    "--days",
    type=int,
    default=30,
    help="Reporting period length in days (default: 30).",
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output PDF path.",
)
def convergence(
    end_date: date | None,
    days: int,
    output: Path | None,
) -> None:
    """Generate a 30-day convergence report PDF."""
    if end_date is None:
        end_date = date.today()
    else:
        end_date = end_date.date()

    start_date = end_date - timedelta(days=days)

    if output is None:
        output = Path(f"convergence_{start_date.isoformat()}_{end_date.isoformat()}.pdf")

    click.echo(f"SMAE Convergence Report — {start_date.isoformat()} / {end_date.isoformat()}")
    click.echo(f"Scanning {days}-day period across all eight metabolic networks...")

    asyncio.run(_run_convergence(start_date, end_date, output))


async def _run_convergence(start_date: date, end_date: date, output: Path) -> None:
    """Run the pipeline and generate a convergence report."""
    from smae.engine.pipeline import AnalyticalPipeline
    from smae.pdf.generator import generate_convergence_report

    sources = _build_sources()
    pipeline = AnalyticalPipeline(sources=sources)

    try:
        result = await pipeline.run(start_date)
    finally:
        for src in sources:
            await src.close()

    if not result.events:
        click.echo(
            "\nNo events returned from configured sources. "
            "Check credentials and network connectivity."
        )
        click.echo("Generating empty convergence report template...")
    else:
        click.echo(
            f"\n{len(result.events)} events ingested, "
            f"{len(result.convergence_nodes)} convergence nodes, "
            f"{len(result.threshold_crossings)} threshold crossings."
        )

    generate_convergence_report(
        events=result.events,
        convergence_scores=result.convergence_nodes,
        period_start=start_date,
        period_end=end_date,
        executive_summary=(
            "No events ingested. Check data source credentials and connectivity."
            if not result.events
            else f"{len(result.events)} events analyzed across "
            f"{len(set(n for e in result.events for n in e.networks))} metabolic networks "
            f"over {(end_date - start_date).days}-day period. "
            f"{len(result.threshold_crossings)} threshold crossings detected. "
            f"{len(result.convergence_nodes)} convergence nodes identified."
        ),
        outlook_rows=[],
        output_path=output,
    )
    click.echo(f"Convergence report written to {output}")


@cli.command()
def networks() -> None:
    """List the eight metabolic networks."""
    from smae.models.enums import MetabolicNetwork

    for n in MetabolicNetwork:
        click.echo(f"  {n.roman:>4}  {n.label}")


@cli.command()
def thresholds() -> None:
    """List all analytical thresholds."""
    from smae.models.thresholds import ALL_THRESHOLDS

    current_category = None
    for t in ALL_THRESHOLDS:
        if t.category != current_category:
            current_category = t.category
            click.echo(f"\n  [{t.category.value.upper()}]")
        click.echo(f"    {t.name:<40} {t.threshold_value:>10,.1f} {t.unit}")


@cli.command()
def sources() -> None:
    """List available data source adapters."""
    from smae.models.enums import SourceTier

    adapters = [
        ("acled", "ACLED — Armed Conflict Location & Event Data", SourceTier.SPECIALIZED_RESEARCH),
        ("gfw", "Global Forest Watch — Deforestation alerts", SourceTier.SPECIALIZED_RESEARCH),
        ("idmc", "IDMC — Internal Displacement Monitoring Centre", SourceTier.UN_OPERATIONAL),
    ]
    click.echo("Available data source adapters:\n")
    for name, desc, tier in adapters:
        click.echo(f"  {name:<8}  [Tier {tier.value}]  {desc}")
    click.echo(
        "\nConfigure credentials via environment variables:"
        "\n  ACLED:  SMAE_ACLED_EMAIL, SMAE_ACLED_PASSWORD  (OAuth account)"
        "\n  GFW:    SMAE_GFW_KEY                           (API key, optional)"
        "\n  IDMC:   SMAE_IDMC_KEY                          (API key, optional)"
    )


@cli.command()
@click.option("--host", default="127.0.0.1", help="Bind host.")
@click.option("--port", "-p", default=8000, help="Bind port.")
@click.option(
    "--static",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to built frontend static files (dashboard/dist).",
)
def serve(host: str, port: int, static: Path | None) -> None:
    """Start the SMAE dashboard web server."""
    import uvicorn

    from smae.api.app import create_app

    app = create_app(static_dir=static)
    click.echo(f"SMAE Dashboard — http://{host}:{port}")
    click.echo("API docs at /docs")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
