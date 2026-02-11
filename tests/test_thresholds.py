"""Tests for SMAE threshold definitions."""

from smae.models.enums import MetabolicNetwork, ThresholdCategory
from smae.models.thresholds import ALL_THRESHOLDS


class TestThresholdDefinitions:
    def test_all_thresholds_loaded(self):
        assert len(ALL_THRESHOLDS) == 16

    def test_absolute_thresholds_count(self):
        absolute = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.ABSOLUTE]
        assert len(absolute) == 5

    def test_rate_of_change_thresholds_count(self):
        roc = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.RATE_OF_CHANGE]
        assert len(roc) == 4

    def test_relational_thresholds_count(self):
        rel = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.RELATIONAL]
        assert len(rel) == 3

    def test_governance_decay_thresholds_count(self):
        gov = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.GOVERNANCE_DECAY]
        assert len(gov) == 4

    def test_all_thresholds_have_networks(self):
        for t in ALL_THRESHOLDS:
            assert len(t.networks) > 0, f"Threshold {t.name} has no networks"

    def test_displacement_bright_line_value(self):
        disp = next(t for t in ALL_THRESHOLDS if t.name == "displacement_single_event")
        assert disp.threshold_value == 100_000
        assert disp.unit == "persons"

    def test_defender_killings_value(self):
        dk = next(t for t in ALL_THRESHOLDS if t.name == "defender_killings")
        assert dk.threshold_value == 5
