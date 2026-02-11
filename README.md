# SMAE — Socio-Metabolic Analytical Engine

Tracking global resource appropriation, cost displacement, and frontline resistance across eight metabolic networks.

## Networks

| # | Network | Domain |
|---|---------|--------|
| I | Carbon Accumulation | Fossil carbon extraction, combustion, trade, deforestation emissions |
| II | Water Appropriation | Freshwater extraction, diversion, commodification, contamination |
| III | Soil Fertility Transfer | Industrial agriculture nutrient extraction and export |
| IV | Mineral Extraction | Metals, rare earths, energy transition minerals |
| V | Atmospheric Commons Degradation | Industrial emissions degrading shared atmospheric commons |
| VI | Biodiversity & Genetic Commons | Bioprospecting, genetic resource extraction, habitat destruction, DSI enclosure |
| VII | Ocean & Marine Appropriation | Fisheries depletion, deep-sea mining, marine contamination, coastal displacement |
| VIII | Labor & Embodied Health | Forced/bonded labor, occupational hazard externalization, labor rights governance |

## Install

```bash
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
```

Available data sources:

| Source | Env Vars | Required |
|--------|----------|----------|
| ACLED | `SMAE_ACLED_EMAIL`, `SMAE_ACLED_PASSWORD` | Both |
| GFW | `SMAE_GFW_KEY` | Optional (rate-limited without) |
| IDMC | `SMAE_IDMC_KEY` | Optional |

## Usage

```bash
smae networks       # List all eight metabolic networks
smae thresholds     # List analytical thresholds (25 across all networks)
smae sources        # List available data source adapters
smae briefing       # Generate daily briefing PDF
smae convergence    # Generate 30-day convergence report PDF
```

### Daily Briefing

```bash
smae briefing                          # Today, 2-day lookback
smae briefing --date 2026-02-01        # Specific date
smae briefing -l 7 -o weekly.pdf       # 7-day lookback, custom output
```

### Convergence Report

```bash
smae convergence                       # 30-day period ending today
smae convergence --days 60             # 60-day period
smae convergence --end-date 2026-01-31 --days 30 -o jan_report.pdf
```

## Tests

```bash
pytest
```

## Architecture

```
smae/
  models/      Core data models (events, thresholds, convergence, enums)
  engine/      Analytical pipeline (7-stage workflow, concurrent source intake)
  sources/     Data source adapters (ACLED, GFW, IDMC)
  pdf/         PDF generation (daily briefing, flash alert, convergence report)
  cli/         Command-line interface
```
