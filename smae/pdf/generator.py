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

from smae.models.convergence import ConvergenceScore
from smae.models.enums import AlertLevel, CouplingPattern, MetabolicNetwork, ThresholdStatus
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
    """Generate a Daily Briefing PDF across all eight metabolic networks.

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


def _network_status_table(events: Sequence[Event]) -> Table:
    """Build an 8-network status matrix: network x event count / CI / alert level."""
    rows = [["Network", "Events", "CI >= 2", "Threshold Crossings", "Max Alert"]]
    for network in MetabolicNetwork:
        net_events = [e for e in events if network in e.networks]
        convergent = [e for e in net_events if e.convergence_index >= 2]
        crossings = sum(len(e.threshold_crossings) for e in net_events)
        max_alert = max(
            (e.alert_level for e in net_events),
            key=lambda a: list(AlertLevel).index(a),
            default=AlertLevel.WATCH,
        )
        rows.append([
            f"{network.roman}: {network.label}",
            str(len(net_events)),
            str(len(convergent)),
            str(crossings),
            max_alert.value,
        ])

    table = Table(rows, repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, "grey"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, row in enumerate(rows[1:], start=1):
        if row[-1] in (AlertLevel.CRITICAL.value, AlertLevel.SYSTEMIC.value):
            style_commands.append(("TEXTCOLOR", (0, i), (-1, i), DARK_RED))
    table.setStyle(TableStyle(style_commands))
    return table


def _convergence_matrix(
    events: Sequence[Event],
    convergence_scores: Sequence[ConvergenceScore],
) -> Optional[Table]:
    """Build a convergence node table showing high-CI events."""
    ci_map = {cs.event_id: cs for cs in convergence_scores}
    high_ci = [
        (e, ci_map[e.id])
        for e in events
        if e.id in ci_map and ci_map[e.id].ci_score >= 2
    ]
    if not high_ci:
        return None

    high_ci.sort(key=lambda x: x[1].ci_score, reverse=True)
    rows = [["Event", "Country", "CI", "Networks", "Classification", "Alert"]]
    for event, cs in high_ci[:20]:
        rows.append([
            event.title[:50],
            event.country,
            f"{cs.ci_score:.1f}",
            ", ".join(n.roman for n in sorted(set(event.networks))),
            cs.classification,
            event.alert_level.value,
        ])

    table = Table(rows, repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK_AMBER),
        ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("GRID", (0, 0), (-1, -1), 0.5, "grey"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, row in enumerate(rows[1:], start=1):
        if row[-1] == AlertLevel.SYSTEMIC.value:
            style_commands.append(("TEXTCOLOR", (0, i), (-1, i), DARK_RED))
    table.setStyle(TableStyle(style_commands))
    return table


def _coupling_pattern_section(
    events: Sequence[Event],
    ss: object,
) -> list:
    """Build the structural coupling patterns analysis section."""
    stylesheet = get_smae_stylesheet()
    elements: list = []

    pattern_events: dict[CouplingPattern, list[Event]] = {}
    for event in events:
        for pattern in event.coupling_patterns:
            pattern_events.setdefault(pattern, []).append(event)

    if not pattern_events:
        elements.append(Paragraph(
            "No structural coupling patterns identified in this reporting period. "
            "Pattern tagging requires analyst review of raw event data.",
            stylesheet["Body"],
        ))
        return elements

    for pattern in sorted(pattern_events, key=lambda p: len(pattern_events[p]), reverse=True):
        evts = pattern_events[pattern]
        countries = sorted(set(e.country for e in evts))
        elements.append(Paragraph(
            f"Pattern {pattern.value}: {pattern.label} ({len(evts)} events)",
            stylesheet["SubHead"],
        ))
        elements.append(Paragraph(
            f"Active in: {', '.join(countries)}. "
            f"Networks involved: "
            f"{', '.join(sorted(set(n.roman for e in evts for n in e.networks)))}.",
            stylesheet["Body"],
        ))
        resistance_events = [
            e for e in evts
            if e.resistance_summary and "[PENDING]" not in e.resistance_summary
        ]
        if resistance_events:
            elements.append(Paragraph(
                f"Contestation: {resistance_events[0].resistance_summary}",
                stylesheet["Resistance"],
            ))

    return elements


def generate_convergence_report(
    events: Sequence[Event],
    convergence_scores: Sequence[ConvergenceScore],
    period_start: date,
    period_end: date,
    executive_summary: str,
    outlook_rows: Sequence[tuple[str, str, str]],
    output_path: Optional[Path] = None,
) -> Path:
    """Generate a Convergence Report PDF (8-15 pages, 30-day cycle).

    Cross-network analysis across all eight metabolic networks, convergence
    nodes, structural coupling patterns, and 90-day outlook.

    Args:
        events: All events in the reporting period, tagged by network.
        convergence_scores: Pre-computed convergence scores for events.
        period_start: Start of the 30-day reporting period.
        period_end: End of the reporting period.
        executive_summary: 3-5 sentence executive summary.
        outlook_rows: Sequence of (domain, trend, key_factor) tuples for 90-day outlook.
        output_path: Where to write the PDF.
    """
    if output_path is None:
        output_path = Path(
            f"convergence_{period_start.isoformat()}_{period_end.isoformat()}.pdf"
        )

    doc = _build_doc(output_path)
    ss = get_smae_stylesheet()
    story: list = []

    # === TITLE ===
    story.append(Paragraph("SMAE CONVERGENCE REPORT", ss["BriefTitle"]))
    story.append(Paragraph(
        f"Period: {period_start.isoformat()} / {period_end.isoformat()}",
        ss["Body"],
    ))
    story.append(Spacer(1, 3 * mm))

    # === EXECUTIVE SUMMARY ===
    story.append(Paragraph("EXECUTIVE SUMMARY", ss["SectionHead"]))
    story.append(Paragraph(executive_summary, ss["ExecSummary"]))
    story.append(Spacer(1, 2 * mm))

    # === NETWORK STATUS MATRIX ===
    story.append(Paragraph(
        "NETWORK STATUS MATRIX — ALL EIGHT METABOLIC NETWORKS",
        ss["SectionHead"],
    ))
    story.append(_network_status_table(events))
    story.append(Spacer(1, 3 * mm))

    # === THRESHOLD DASHBOARD ===
    threshold_table = _threshold_table(events, ss)
    if threshold_table:
        story.append(Paragraph("THRESHOLD DASHBOARD", ss["SectionHead"]))
        story.append(threshold_table)
        story.append(Spacer(1, 3 * mm))

    # === CONVERGENCE ANALYSIS ===
    story.append(Paragraph("CONVERGENCE ANALYSIS", ss["SectionHead"]))
    ci_map = {cs.event_id: cs for cs in convergence_scores}
    systemic_nodes = [
        (e, ci_map[e.id]) for e in events
        if e.id in ci_map and ci_map[e.id].ci_score >= 4
    ]
    multi_nodes = [
        (e, ci_map[e.id]) for e in events
        if e.id in ci_map and 2 <= ci_map[e.id].ci_score < 4
    ]

    summary_parts = [
        f"{len(events)} events analyzed across "
        f"{len(set(n for e in events for n in e.networks))} metabolic networks."
    ]
    if systemic_nodes:
        summary_parts.append(
            f"{len(systemic_nodes)} systemic nodes identified (CI >= 4) — "
            f"requiring immediate structural analysis."
        )
    if multi_nodes:
        summary_parts.append(
            f"{len(multi_nodes)} multi-network convergence events (CI 2-3) "
            f"flagged for cross-network escalation."
        )
    story.append(Paragraph(" ".join(summary_parts), ss["Body"]))

    conv_matrix = _convergence_matrix(events, convergence_scores)
    if conv_matrix:
        story.append(Paragraph("CONVERGENCE NODES", ss["SubHead"]))
        story.append(conv_matrix)
        story.append(Spacer(1, 3 * mm))

    # === SYSTEMIC NODE DETAIL ===
    if systemic_nodes:
        story.append(Paragraph("SYSTEMIC NODE DETAIL", ss["SectionHead"]))
        for event, cs in sorted(systemic_nodes, key=lambda x: x[1].ci_score, reverse=True):
            story.append(Paragraph(
                f"{event.country}: {event.title} (CI {cs.ci_score:.1f})",
                ss["SubHead"],
            ))
            story.append(Paragraph(event.summary, ss["Body"]))
            story.append(Paragraph(f"Networks: {event.network_labels}", ss["Body"]))
            for tc in event.threshold_crossings:
                story.append(Paragraph(tc.metric.comparison_string, ss["Metric"]))
            if event.resistance_summary:
                story.append(Paragraph(
                    f"Resistance: {event.resistance_summary}",
                    ss["Resistance"],
                ))
            if event.governance_context:
                story.append(Paragraph(
                    f"Governance: {event.governance_context}",
                    ss["Body"],
                ))
        story.append(Spacer(1, 3 * mm))

    # === CROSS-NETWORK ANALYSIS BY DOMAIN ===
    story.append(Paragraph("CROSS-NETWORK ANALYSIS BY DOMAIN", ss["SectionHead"]))
    for network in MetabolicNetwork:
        net_events = [e for e in events if network in e.networks]
        if not net_events:
            continue

        convergent = [e for e in net_events if e.convergence_index >= 2]
        story.append(Paragraph(
            f"NETWORK {network.roman}: {network.label.upper()} "
            f"({len(net_events)} events, {len(convergent)} convergent)",
            ss["SubHead"],
        ))

        sorted_events = sorted(
            net_events,
            key=lambda e: list(AlertLevel).index(e.alert_level),
            reverse=True,
        )
        for event in sorted_events[:5]:
            style = ss["Alert"] if event.alert_level in (
                AlertLevel.ALERT, AlertLevel.CRITICAL, AlertLevel.SYSTEMIC
            ) else ss["Body"]
            story.append(Paragraph(
                f"[{event.alert_level.value}] {event.country}: {event.title}",
                style,
            ))
            if event.resistance_summary and "[PENDING]" not in event.resistance_summary:
                story.append(Paragraph(
                    f"Resistance: {event.resistance_summary}",
                    ss["Resistance"],
                ))

    story.append(Spacer(1, 3 * mm))

    # === STRUCTURAL COUPLING PATTERNS ===
    story.append(Paragraph("STRUCTURAL COUPLING PATTERNS", ss["SectionHead"]))
    story.extend(_coupling_pattern_section(events, ss))
    story.append(Spacer(1, 3 * mm))

    # === RESISTANCE ANALYSIS ===
    story.append(Paragraph("RESISTANCE ANALYSIS", ss["SectionHead"]))
    resistance_events = [
        e for e in events
        if e.resistance_summary and "[PENDING]" not in e.resistance_summary
    ]
    if resistance_events:
        story.append(Paragraph(
            f"{len(resistance_events)} events with documented resistance activity. "
            f"Resistance is primary evidence of system stress points, alternative "
            f"governance, and trajectory indicators.",
            ss["Body"],
        ))
        for event in resistance_events[:10]:
            story.append(Paragraph(
                f"{event.country} — {event.title}", ss["SubHead"],
            ))
            story.append(Paragraph(event.resistance_summary, ss["Resistance"]))
    else:
        story.append(Paragraph(
            "No verified resistance data collected this period. "
            "Frontline/EJ source follow-up required.",
            ss["Body"],
        ))
    story.append(Spacer(1, 3 * mm))

    # === 90-DAY OUTLOOK ===
    story.append(Paragraph("90-DAY OUTLOOK", ss["SectionHead"]))
    if outlook_rows:
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
    else:
        story.append(Paragraph(
            "Outlook data pending analyst review.",
            ss["Body"],
        ))

    # === SOURCE APPENDIX ===
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
