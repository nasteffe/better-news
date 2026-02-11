"""Enumerations for the SMAE analytical framework."""

from enum import Enum, IntEnum


class MetabolicNetwork(IntEnum):
    """The eight metabolic networks through which all events are analyzed."""

    CARBON = 1       # Carbon Accumulation
    WATER = 2        # Water Appropriation
    SOIL = 3         # Soil Fertility Transfer
    MINERAL = 4      # Mineral Extraction
    ATMOSPHERIC = 5  # Atmospheric Commons Degradation
    BIODIVERSITY = 6 # Biodiversity & Genetic Commons
    OCEAN = 7        # Ocean & Marine Appropriation
    LABOR = 8        # Labor & Embodied Health

    @property
    def label(self) -> str:
        labels = {
            1: "Carbon Accumulation",
            2: "Water Appropriation",
            3: "Soil Fertility Transfer",
            4: "Mineral Extraction",
            5: "Atmospheric Commons Degradation",
            6: "Biodiversity & Genetic Commons",
            7: "Ocean & Marine Appropriation",
            8: "Labor & Embodied Health",
        }
        return labels[self.value]

    @property
    def roman(self) -> str:
        numerals = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
            6: "VI", 7: "VII", 8: "VIII",
        }
        return numerals[self.value]


class AnalyticalLayer(str, Enum):
    """Six-layer schema applied to each metabolic network."""

    STOCK = "stock"
    FLOW = "flow"
    ACCUMULATION = "accumulation"
    EXTERNALITY = "externality"
    GOVERNANCE = "governance"
    CONTESTATION = "contestation"


class OntologyNode(str, Enum):
    """Four-node decomposition applied to every event."""

    APPROPRIATION = "appropriation"
    DISPLACEMENT = "displacement"
    GOVERNANCE = "governance"
    RESISTANCE = "resistance"


class AlertLevel(str, Enum):
    """Triage classification for analytical products."""

    WATCH = "WATCH"
    MONITOR = "MONITOR"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"
    SYSTEMIC = "SYSTEMIC"


class ThresholdStatus(str, Enum):
    """Whether a threshold has been crossed."""

    BELOW = "BELOW"
    APPROACHING = "APPROACHING"  # Within 20% of threshold
    EXCEEDED = "EXCEEDED"


class ThresholdCategory(str, Enum):
    """Categories of analytical thresholds."""

    ABSOLUTE = "absolute"
    RATE_OF_CHANGE = "rate_of_change"
    RELATIONAL = "relational"
    GOVERNANCE_DECAY = "governance_decay"


class SourceTier(IntEnum):
    """Source hierarchy — strict priority order."""

    FRONTLINE_EJ = 1
    INDIGENOUS_MONITORING = 2
    UN_OPERATIONAL = 3
    SPECIALIZED_RESEARCH = 4
    ACADEMIC_PEER_REVIEWED = 5
    INVESTIGATIVE_MEDIA = 6
    GOVERNMENT_REGULATORY = 7


class CouplingPattern(IntEnum):
    """Eleven structural coupling patterns tracked across cases."""

    EXTRACTIVE_CASCADE = 1
    REGULATORY_ARBITRAGE = 2
    GREEN_TRANSITION_PARADOX = 3
    ATMOSPHERIC_ENCLOSURE = 4
    DEBT_NATURE_TRAP = 5
    SACRIFICE_ZONE_SPIRAL = 6
    MILITARIZED_CONSERVATION = 7
    FOOD_SOVEREIGNTY_EROSION = 8
    HUMANITARIAN_SECURITY_FEEDBACK = 9
    KNOWLEDGE_ENCLOSURE = 10
    INFRASTRUCTURE_LOCKIN = 11

    @property
    def label(self) -> str:
        labels = {
            1: "Extractive Cascade",
            2: "Regulatory Arbitrage Loop",
            3: "Green Transition Paradox",
            4: "Atmospheric Enclosure",
            5: "Debt-Nature Trap",
            6: "Sacrifice Zone Intensification Spiral",
            7: "Militarized Conservation Enclosure",
            8: "Food Sovereignty Erosion Loop",
            9: "Humanitarian-Security Feedback",
            10: "Knowledge Enclosure Circuit",
            11: "Infrastructure Lock-in Ratchet",
        }
        return labels[self.value]
