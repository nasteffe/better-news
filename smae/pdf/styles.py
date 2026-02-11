"""PDF paragraph styles as specified in the SMAE formatting standards."""

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import mm

# SMAE color palette
DARK_RED = HexColor("#8b0000")       # Appropriation / displacement
DARK_GREEN = HexColor("#006400")     # Resistance
DARK_BLUE = HexColor("#16537e")      # Governance / section headers
DARK_AMBER = HexColor("#b8860b")     # Convergence alerts
BODY_COLOR = HexColor("#222222")
SUBHEAD_COLOR = HexColor("#333333")
TITLE_COLOR = HexColor("#1a1a2e")
METRIC_COLOR = HexColor("#333333")
SOURCE_COLOR = HexColor("#555555")


def get_smae_stylesheet() -> StyleSheet1:
    """Build the SMAE stylesheet with all specified paragraph styles."""
    styles = StyleSheet1()

    styles.add(ParagraphStyle(
        name="BriefTitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=TITLE_COLOR,
        spaceAfter=6 * mm,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="SectionHead",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=DARK_BLUE,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="SubHead",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        textColor=SUBHEAD_COLOR,
        spaceBefore=3 * mm,
        spaceAfter=1.5 * mm,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="Body",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=BODY_COLOR,
        spaceAfter=2 * mm,
        alignment=TA_JUSTIFY,
        leading=11,
    ))

    styles.add(ParagraphStyle(
        name="Alert",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        textColor=DARK_RED,
        spaceAfter=2 * mm,
        alignment=TA_LEFT,
        leading=11,
    ))

    styles.add(ParagraphStyle(
        name="Resistance",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        textColor=DARK_GREEN,
        spaceAfter=2 * mm,
        alignment=TA_LEFT,
        leading=11,
    ))

    styles.add(ParagraphStyle(
        name="Metric",
        fontName="Courier",
        fontSize=8,
        textColor=METRIC_COLOR,
        spaceAfter=1.5 * mm,
        alignment=TA_LEFT,
        leading=10,
    ))

    styles.add(ParagraphStyle(
        name="Source",
        fontName="Helvetica",
        fontSize=7,
        textColor=SOURCE_COLOR,
        spaceAfter=1 * mm,
        alignment=TA_LEFT,
        leading=9,
    ))

    styles.add(ParagraphStyle(
        name="ExecSummary",
        fontName="Helvetica",
        fontSize=9,
        textColor=BODY_COLOR,
        spaceAfter=3 * mm,
        alignment=TA_JUSTIFY,
        leading=12,
    ))

    return styles
