"""Threshold definitions from the SMAE specification.

Defines the bright-line, rate-of-change, relational, and governance decay
thresholds used for analytical triage.
"""

from __future__ import annotations

from dataclasses import dataclass

from smae.models.enums import MetabolicNetwork, ThresholdCategory


@dataclass(frozen=True)
class ThresholdDefinition:
    """A defined analytical threshold from the SMAE specification."""

    name: str
    category: ThresholdCategory
    description: str
    networks: tuple[MetabolicNetwork, ...]
    threshold_value: float
    unit: str


# --- Absolute (Bright Lines) ---

DISPLACEMENT_BRIGHT_LINE = ThresholdDefinition(
    name="displacement_single_event",
    category=ThresholdCategory.ABSOLUTE,
    description="Displacement >100 000 persons in single event/campaign",
    networks=(MetabolicNetwork.CARBON, MetabolicNetwork.WATER, MetabolicNetwork.MINERAL),
    threshold_value=100_000,
    unit="persons",
)

CONTAMINATION_BRIGHT_LINE = ThresholdDefinition(
    name="contamination_who_limits",
    category=ThresholdCategory.ABSOLUTE,
    description="Contamination above WHO limits affecting >50 000 persons",
    networks=(MetabolicNetwork.WATER, MetabolicNetwork.ATMOSPHERIC),
    threshold_value=50_000,
    unit="persons",
)

ARMED_CONFLICT_BRIGHT_LINE = ThresholdDefinition(
    name="armed_conflict_fatalities",
    category=ThresholdCategory.ABSOLUTE,
    description="Armed conflict >1 000 fatalities in 30-day window",
    networks=(MetabolicNetwork.MINERAL, MetabolicNetwork.CARBON),
    threshold_value=1_000,
    unit="fatalities/30d",
)

REGULATORY_ROLLBACK_BRIGHT_LINE = ThresholdDefinition(
    name="regulatory_rollback",
    category=ThresholdCategory.ABSOLUTE,
    description="Regulatory rollback eliminating >10% governance coverage in any network",
    networks=tuple(MetabolicNetwork),
    threshold_value=10,
    unit="% governance coverage",
)

DEFENDER_KILLINGS_BRIGHT_LINE = ThresholdDefinition(
    name="defender_killings",
    category=ThresholdCategory.ABSOLUTE,
    description="Land/environmental defender killings >5 in 90-day window per jurisdiction",
    networks=tuple(MetabolicNetwork),
    threshold_value=5,
    unit="killings/90d/jurisdiction",
)

# --- Rate-of-Change (Velocity) ---

DISPLACEMENT_RATE_DOUBLING = ThresholdDefinition(
    name="displacement_rate_doubling",
    category=ThresholdCategory.RATE_OF_CHANGE,
    description="Displacement rate doubling within 30-day window",
    networks=tuple(MetabolicNetwork),
    threshold_value=2.0,
    unit="rate multiplier/30d",
)

DEFORESTATION_SIGMA = ThresholdDefinition(
    name="deforestation_anomaly",
    category=ThresholdCategory.RATE_OF_CHANGE,
    description="Deforestation >3 sigma above 5-year mean for any jurisdiction",
    networks=(MetabolicNetwork.CARBON, MetabolicNetwork.SOIL),
    threshold_value=3.0,
    unit="sigma above 5y mean",
)

CONFLICT_FATALITIES_ACCELERATION = ThresholdDefinition(
    name="conflict_fatalities_acceleration",
    category=ThresholdCategory.RATE_OF_CHANGE,
    description="Conflict fatalities >50% month-on-month for 3 consecutive months",
    networks=(MetabolicNetwork.MINERAL, MetabolicNetwork.CARBON),
    threshold_value=50,
    unit="% MoM increase",
)

REGULATORY_ROLLBACK_CLUSTER = ThresholdDefinition(
    name="regulatory_rollback_cluster",
    category=ThresholdCategory.RATE_OF_CHANGE,
    description="3 significant regulatory rollbacks in single jurisdiction within 60 days",
    networks=tuple(MetabolicNetwork),
    threshold_value=3,
    unit="rollbacks/60d",
)

# --- Relational (Equity) ---

EMISSIONS_INEQUITY = ThresholdDefinition(
    name="emissions_inequity",
    category=ThresholdCategory.RELATIONAL,
    description=(
        "Per capita emissions of A >20x B, where B bears >5x climate vulnerability"
    ),
    networks=(MetabolicNetwork.CARBON, MetabolicNetwork.ATMOSPHERIC),
    threshold_value=20,
    unit="emissions ratio",
)

CORPORATE_WATER_EXTRACTION = ThresholdDefinition(
    name="corporate_water_vs_domestic",
    category=ThresholdCategory.RELATIONAL,
    description=(
        "Corporate water extraction exceeding domestic supply for community >10 000 persons"
    ),
    networks=(MetabolicNetwork.WATER,),
    threshold_value=1.0,
    unit="extraction/supply ratio",
)

EJ_POLLUTION_EXPOSURE = ThresholdDefinition(
    name="ej_pollution_exposure",
    category=ThresholdCategory.RELATIONAL,
    description="EJ community pollution exposure >3x jurisdictional mean",
    networks=(MetabolicNetwork.ATMOSPHERIC,),
    threshold_value=3.0,
    unit="exposure ratio",
)

# --- Governance Decay (Institutional) ---

TREATY_NONCOMPLIANCE = ThresholdDefinition(
    name="treaty_noncompliance",
    category=ThresholdCategory.GOVERNANCE_DECAY,
    description="Treaty withdrawal or non-compliance",
    networks=tuple(MetabolicNetwork),
    threshold_value=1,
    unit="event",
)

AGENCY_BUDGET_CUT = ThresholdDefinition(
    name="agency_budget_cut",
    category=ThresholdCategory.GOVERNANCE_DECAY,
    description="Regulatory agency budget/staffing cut >20%",
    networks=tuple(MetabolicNetwork),
    threshold_value=20,
    unit="% cut",
)

FPIC_WEAKENED = ThresholdDefinition(
    name="fpic_weakened",
    category=ThresholdCategory.GOVERNANCE_DECAY,
    description="FPIC requirement removed or weakened",
    networks=tuple(MetabolicNetwork),
    threshold_value=1,
    unit="event",
)

WHISTLEBLOWER_PROTECTION_ELIMINATED = ThresholdDefinition(
    name="whistleblower_protection_eliminated",
    category=ThresholdCategory.GOVERNANCE_DECAY,
    description="Whistleblower/transparency protection eliminated",
    networks=tuple(MetabolicNetwork),
    threshold_value=1,
    unit="event",
)


# All thresholds for iteration
ALL_THRESHOLDS: list[ThresholdDefinition] = [
    DISPLACEMENT_BRIGHT_LINE,
    CONTAMINATION_BRIGHT_LINE,
    ARMED_CONFLICT_BRIGHT_LINE,
    REGULATORY_ROLLBACK_BRIGHT_LINE,
    DEFENDER_KILLINGS_BRIGHT_LINE,
    DISPLACEMENT_RATE_DOUBLING,
    DEFORESTATION_SIGMA,
    CONFLICT_FATALITIES_ACCELERATION,
    REGULATORY_ROLLBACK_CLUSTER,
    EMISSIONS_INEQUITY,
    CORPORATE_WATER_EXTRACTION,
    EJ_POLLUTION_EXPOSURE,
    TREATY_NONCOMPLIANCE,
    AGENCY_BUDGET_CUT,
    FPIC_WEAKENED,
    WHISTLEBLOWER_PROTECTION_ELIMINATED,
]
