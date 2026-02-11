"""PDF document generator for SMAE analytical products.

Generates A4 PDFs using reportlab with the SMAE stylesheet.
Supports Flash Alerts, Flow Briefings, Daily Briefings, and Convergence Reports.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional, Sequence

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from smae.models.enums import AlertLevel, MetabolicNetwork, ThresholdStatus
from smae.models.events import Event, Source
from smae.pdf.styles import (
    DARK_AMBER,
    DARK_BLUE,
    DARK_GREEN,
    DARK_RED,
    get_smae_stylesheet,
)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 18 * mm


def _build_doc(output_path: Path) -> BaseDocTemplate:
    """Create an A4 document with SMAE margins."""
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    frame = Frame(
        MARGIN,
        MARGIN,
        PAGE_WIDTH - 2 * MARGIN,
        PAGE_HEIGHT - 2 * MARGIN,
        id="main",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    return doc


def _threshold_table(events: Sequence[Event], styles: object) -> Optional[Table]:
    """Build a threshold dashboard table from events with crossings."""
    rows = [["Metric", "Baseline", "Delta", "Current", "Threshold", "Status"]]
    has_data = False
    for event in events:
        for tc in event.threshold_crossings:
            m = tc.metric
            status_str = m.status.value
            rows.append([
                m.name,
                f"{m.baseline_value:,.1f} ({m.baseline_date.isoformat()})",
                f"{m.delta:+,.1f}",
                f"{m.current_value:,.1f}",
                f"{m.threshold_value:,.1f}",
                status_str,
            ])
            has_data = True

    if not has_data:
        return None

    table = Table(rows, repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, "grey"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    # Color exceeded rows
    for i, row in enumerate(rows[1:], start=1):
        if row[-1] == ThresholdStatus.EXCEEDED.value:
            style_commands.append(("TEXTCOLOR", (0, i), (-1, i), DARK_RED))

    table.setStyle(TableStyle(style_commands))
    return table


def _source_appendix(sources: Sequence[Source], styles: object) -> list:
    """Build numbered source appendix."""
    ss = get_smae_stylesheet()
    elements = [Paragraph("SOURCE APPENDIX", ss["SectionHead"])]
    for i, src in enumerate(sources, 1):
        prov = " [provisional]" if src.provisional else ""
        elements.append(Paragraph(
            f"[{i}] {src.citation} (accessed {src.access_date.isoformat()}){prov}",
            ss["Source"],
        ))
    return elements


def generate_flash_alert(
    event: Event,
    output_path: Path,
) -> Path:
    """Generate a 1-2 page Flash Alert PDF for a single threshold crossing."""
    doc = _build_doc(output_path)
    ss = get_smae_stylesheet()
    story: list = []

    # Header
    networks_str = ", ".join(n.roman for n in sorted(set(event.networks)))
    story.append(Paragraph(
        f"SMAE FLASH ALERT — {event.event_date.isoformat()}",
        ss["BriefTitle"],
    ))
    story.append(Paragraph(
        f"Network(s): {networks_str}  |  CI: {event.convergence_index}  "
        f"|  Level: {event.alert_level.value}",
        ss["Alert"] if event.alert_level in (AlertLevel.CRITICAL, AlertLevel.SYSTEMIC)
        else ss["Body"],
    ))
    story.append(Spacer(1, 3 * mm))

    # Event
    story.append(Paragraph("EVENT", ss["SectionHead"]))
    story.append(Paragraph(event.summary, ss["Body"]))

    # Metabolic context
    story.append(Paragraph("METABOLIC CONTEXT", ss["SectionHead"]))
    story.append(Paragraph(event.network_labels, ss["Body"]))

    # Threshold
    if event.threshold_crossings:
        story.append(Paragraph("THRESHOLD", ss["SectionHead"]))
        for tc in event.threshold_crossings:
            story.append(Paragraph(tc.metric.comparison_string, ss["Metric"]))

    # Convergence
    if event.is_convergence_node:
        story.append(Paragraph("CONVERGENCE", ss["SectionHead"]))
        story.append(Paragraph(
            f"CI {event.convergence_index} — {event.network_labels}",
            ss["Body"],
        ))

    # Resistance
    story.append(Paragraph("RESISTANCE", ss["SectionHead"]))
    story.append(Paragraph(
        event.resistance_summary or "No resistance data available for this event.",
        ss["Resistance"],
    ))

    # Governance
    story.append(Paragraph("GOVERNANCE", ss["SectionHead"]))
    story.append(Paragraph(
        event.governance_context or "Governance context pending analysis.",
        ss["Body"],
    ))

    # Outlook
    story.append(Paragraph("OUTLOOK (30 DAYS)", ss["SectionHead"]))
    story.append(Paragraph(
        event.outlook_30d or "Outlook pending further data.",
        ss["Body"],
    ))

    # Sources
    if event.sources:
        story.extend(_source_appendix(event.sources, ss))

    doc.build(story)
    return output_path


def generate_daily_briefing(
    events: Sequence[Event],
    briefing_date: date,
    executive_summary: str,
    outlook_rows: Sequence[tuple[str, str, str]],
    output_path: Optional[Path] = None,
) -> Path:
    """Generate a Daily Briefing PDF across all five metabolic networks.

    Args:
        events: All events to include, tagged by network.
        briefing_date: The date of the briefing.
        executive_summary: 3-5 sentence executive summary.
        outlook_rows: Sequence of (domain, trend, key_factor) tuples for 30-day outlook.
        output_path: Where to write the PDF. Defaults to briefing_YYYY-MM-DD.pdf.
    """
    if output_path is None:
        output_path = Path(f"briefing_{briefing_date.isoformat()}.pdf")

    doc = _build_doc(output_path)
    ss = get_smae_stylesheet()
    story: list = []

    # Title
    story.append(Paragraph(
        f"SMAE DAILY BRIEFING — {briefing_date.isoformat()}",
        ss["BriefTitle"],
    ))
    story.append(Spacer(1, 2 * mm))

    # Executive summary
    story.append(Paragraph("EXECUTIVE SUMMARY", ss["SectionHead"]))
    story.append(Paragraph(executive_summary, ss["ExecSummary"]))

    # Threshold dashboard
    threshold_table = _threshold_table(events, ss)
    if threshold_table:
        story.append(Paragraph("THRESHOLD DASHBOARD", ss["SectionHead"]))
        story.append(threshold_table)
        story.append(Spacer(1, 3 * mm))

    # Domain sections (one per network)
    for network in MetabolicNetwork:
        network_events = [e for e in events if network in e.networks]
        if not network_events:
            continue

        story.append(Paragraph(
            f"NETWORK {network.roman}: {network.label.upper()}",
            ss["SectionHead"],
        ))

        for event in network_events:
            story.append(Paragraph(f"{event.country}: {event.title}", ss["SubHead"]))
            story.append(Paragraph(event.summary, ss["Body"]))

            # Threshold crossings inline
            for tc in event.threshold_crossings:
                story.append(Paragraph(tc.metric.comparison_string, ss["Metric"]))

            # Resistance inline (not separate section)
            if event.resistance_summary:
                story.append(Paragraph(
                    f"Resistance: {event.resistance_summary}",
                    ss["Resistance"],
                ))

    # 30-day outlook table
    if outlook_rows:
        story.append(Paragraph("30-DAY OUTLOOK", ss["SectionHead"]))
        header = ["Domain", "Trend", "Key Factor"]
        table_data = [header] + [list(row) for row in outlook_rows]
        outlook_table = Table(table_data, repeatRows=1)
        outlook_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, "grey"),
        ]))
        story.append(outlook_table)

    # Source appendix
    all_sources: list[Source] = []
    seen: set[str] = set()
    for event in events:
        for src in event.sources:
            key = src.citation
            if key not in seen:
                seen.add(key)
                all_sources.append(src)
    if all_sources:
        story.extend(_source_appendix(all_sources, ss))

    doc.build(story)
    return output_path
