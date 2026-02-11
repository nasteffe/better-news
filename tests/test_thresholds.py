"""Tests for SMAE threshold definitions."""

from smae.models.enums import MetabolicNetwork, ThresholdCategory
from smae.models.thresholds import ALL_THRESHOLDS


class TestThresholdDefinitions:
    def test_all_thresholds_loaded(self):
        assert len(ALL_THRESHOLDS) == 25

    def test_absolute_thresholds_count(self):
        absolute = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.ABSOLUTE]
        assert len(absolute) == 9

    def test_rate_of_change_thresholds_count(self):
        roc = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.RATE_OF_CHANGE]
        assert len(roc) == 6

    def test_relational_thresholds_count(self):
        rel = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.RELATIONAL]
        assert len(rel) == 4

    def test_governance_decay_thresholds_count(self):
        gov = [t for t in ALL_THRESHOLDS if t.category == ThresholdCategory.GOVERNANCE_DECAY]
        assert len(gov) == 6

    def test_new_network_thresholds_exist(self):
        names = {t.name for t in ALL_THRESHOLDS}
        # Biodiversity
        assert "species_extinction_rate" in names
        assert "habitat_loss_single_event" in names
        assert "genetic_resource_enclosure" in names
        # Ocean
        assert "fisheries_stock_collapse" in names
        assert "deep_sea_mining_area" in names
        assert "marine_contamination" in names
        # Labor
        assert "forced_labor_incidents" in names
        assert "occupational_fatality_rate" in names
        assert "labor_rights_rollback" in names

    def test_biodiversity_threshold_networks(self):
        bio = [t for t in ALL_THRESHOLDS if MetabolicNetwork.BIODIVERSITY in t.networks]
        assert len(bio) >= 3

    def test_ocean_threshold_networks(self):
        ocean = [t for t in ALL_THRESHOLDS if MetabolicNetwork.OCEAN in t.networks]
        assert len(ocean) >= 3

    def test_labor_threshold_networks(self):
        labor = [t for t in ALL_THRESHOLDS if MetabolicNetwork.LABOR in t.networks]
        assert len(labor) >= 2

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

    def test_forced_labor_bright_line_value(self):
        fl = next(t for t in ALL_THRESHOLDS if t.name == "forced_labor_incidents")
        assert fl.threshold_value == 500
        assert fl.unit == "persons"

    def test_fisheries_collapse_value(self):
        fc = next(t for t in ALL_THRESHOLDS if t.name == "fisheries_stock_collapse")
        assert fc.threshold_value == 20
        assert fc.unit == "% of B0"
