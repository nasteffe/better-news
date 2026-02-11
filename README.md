# SMAE — Socio-Metabolic Analytical Engine

Tracking global resource appropriation, cost displacement, and frontline resistance across five metabolic networks.

## Networks

| # | Network | Domain |
|---|---------|--------|
| I | Carbon Accumulation | Fossil carbon extraction, combustion, trade, deforestation emissions |
| II | Water Appropriation | Freshwater extraction, diversion, commodification, contamination |
| III | Soil Fertility Transfer | Industrial agriculture nutrient extraction and export |
| IV | Mineral Extraction | Metals, rare earths, energy transition minerals |
| V | Atmospheric Commons Degradation | Industrial emissions degrading shared atmospheric commons |

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```bash
smae networks       # List metabolic networks
smae thresholds     # List analytical thresholds
smae sources        # List available data source adapters
smae briefing       # Generate daily briefing PDF
```

## Tests

```bash
pytest
```

## Architecture

```
smae/
  models/      Core data models (events, thresholds, convergence, enums)
  engine/      Analytical pipeline (7-stage workflow)
  sources/     Data source adapters (ACLED, GFW, IDMC)
  pdf/         PDF generation with reportlab
  cli/         Command-line interface
```
