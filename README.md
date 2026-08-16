# Portfolio Optimization

A modular Python application for preparing historical asset prices and building
a portfolio-optimization workflow. The core package is market-agnostic: its
behavior is determined by the price data supplied through configuration.

## Current capabilities

- load and validate historical closing prices from CSV;
- use every asset available in the supplied price dataset;
- calculate daily returns independently for each asset;
- calculate mean returns and a covariance matrix;
- display dataset statistics through a CLI;
- expose a FastAPI health endpoint;
- expose a typed portfolio-analysis endpoint backed by an application service;
- return a consistent 422 error contract for expected domain failures;
- verify behavior using automated tests and neutral fixtures.

SGA and AGA portfolio optimization remain planned work. The current application
prepares optimization-ready statistical inputs but does not select portfolio
weights yet.

## Workflow

```text
Historical price CSV
        |
        v
Load and validate prices
        v
Available asset universe
        |
        v
Daily returns per asset
        |
        v
Mean returns + covariance matrix
        |
        +----> CLI
        +----> future optimization service
        +----> future API endpoints
```

## Project structure

```text
.
├── apps/
│   └── api/                         # FastAPI application
├── data/                            # Local research datasets
├── notebook_raw/                    # Original research notebook
├── src/portfolio_optimization/
│   ├── compute_statistic/           # Returns, means, and covariance
│   ├── ingestion/                   # Historical price loading
│   ├── services/                    # Application workflows
│   ├── cli.py                       # Command-line interface
│   ├── config.py                    # Validated environment configuration
│   └── exceptions.py                # Domain exceptions
├── tests/                           # Automated tests and neutral fixtures
├── .env.example                     # Configuration template
└── pyproject.toml                   # Package and dependency configuration
```

## Requirements

- Python 3.12 or newer
- pip
- a virtual environment

Runtime dependencies are declared in `pyproject.toml` and include pandas,
FastAPI, Uvicorn, and Pydantic Settings. Development dependencies include pytest
and HTTPX.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Editable installation makes Python use the current package under `src/`, so
normal source changes do not require reinstalling the project.

## Configuration

Copy the configuration template:

```bash
cp .env.example .env
```

Configure the local data paths:

```env
PRICE_DATA_PATH=data/prices.csv
```

`PRICE_DATA_PATH` is required. Every ticker in that dataset is included in the
portfolio-statistics calculation.

The local `.env` file is ignored by Git. `.env.example` documents the available
settings without containing machine-specific values or secrets.

### Price data contract

```csv
Date,ticker,Close
2025-01-02,AAA,100.0
2025-01-03,AAA,105.0
```

## Run the CLI

```bash
python -m portfolio_optimization
```

Or without activating the virtual environment:

```bash
.venv/bin/python -m portfolio_optimization
```

Example output:

```text
Portfolio Dataset Summary
Rows        : 6
Tickers     : 2
Start date  : 2025-01-02
End date    : 2025-01-06
Missing     : 0
Portfolio Statistics
Return rows : 2
Assets      : 2
Covariance  : 2 x 2
```

## Run the API

```bash
uvicorn apps.api.main:app --reload
```

- Health endpoint: <http://127.0.0.1:8000/health>
- Interactive documentation: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

Current health response:

```json
{"status": "ok"}
```

Portfolio analysis endpoint: <http://127.0.0.1:8000/portfolio/analysis>

Expected domain and input-data failures use this response shape with HTTP 422:

```json
{
  "error": {
    "code": "data_validation_error",
    "message": "Missing required columns: ['Close']"
  }
}
```

## Run tests

Run everything:

```bash
.venv/bin/pytest -q
```

Run individual areas:

```bash
.venv/bin/pytest -q tests/test_portfolio_statistics.py
.venv/bin/pytest -q tests/test_api_health.py
```

Tests use small neutral symbols such as `AAA` and `BBB`; they do not depend on a
specific stock exchange or index.

## Design boundary

The package contains general portfolio logic. A particular market, exchange,
index, date range, or research dataset belongs in configuration and data—not in
module names or domain behavior.

```text
General code
    + market-specific data
    + environment configuration
    = a concrete portfolio experiment
```

This keeps the same package reusable for any collection of assets supplied in a
valid price dataset.

## Planned work

- complete missing-value and duplicate-observation policies;
- add configurable date ranges and time-based dataset splitting;
- implement portfolio constraints and fitness calculations;
- modularize SGA and AGA;
- add backtesting and evaluation;
- expose an optimization API endpoint;
- add deployment configuration after the API contract stabilizes.
