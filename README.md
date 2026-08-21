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
- manage Assets and historical PriceReadings through typed service boundaries;
- execute the notebook-derived Standard Genetic Algorithm (SGA);
- persist OptimizationRuns and Allocations atomically in memory;
- return a consistent 422 error contract for expected domain failures;
- verify behavior using automated tests and neutral fixtures.
- create and reload persisted portfolio briefs through the v0.1 Next.js slice;
- return deterministic AI-stub guidance for each brief risk profile.

AGA remains planned work. SGA selects long-only portfolio weights whose total
is one and whose maximum allocation per asset is configurable.

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
        v
Standard Genetic Algorithm
        |
        v
OptimizationRun + Allocations
```

## Project structure

```text
.
├── apps/
│   └── api/                         # FastAPI application
├── data/                            # Local research datasets
├── docs/                            # Architecture and relational design
├── notebooks/                       # Research and experiment notebooks
├── src/portfolio_optimization/
│   ├── analytics/                   # Returns, means, and covariance
│   ├── domain/                      # Entities grouped by domain concept
│   ├── ingestion/                   # Historical price loading
│   ├── optimization/                # Standard Genetic Algorithm
│   ├── repositories/                # Contracts and in-memory storage
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

Runtime dependencies are declared in `pyproject.toml` and include NumPy,
pandas, FastAPI, Uvicorn, and Pydantic Settings. Development dependencies
include pytest and HTTPX.

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
DATABASE_URL=postgresql+psycopg://portfolio:portfolio@localhost:5432/portfolio
DATABASE_ECHO=false
```

`PRICE_DATA_PATH` is required. Every ticker in that dataset is included in the
portfolio-statistics calculation.

`DATABASE_URL` selects the PostgreSQL database. Apply the baseline schema with
`alembic upgrade head`. `/health` checks process liveness, while `/health/db`
runs `SELECT 1` against the configured database.

The table, constraint, index, and migration-chain notes are documented in
[docs/database-schema.md](docs/database-schema.md).

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

## Run the v0.1 web slice

Start PostgreSQL and apply both migrations before starting the API:

```bash
docker compose up -d postgres
.venv/bin/alembic upgrade head
.venv/bin/uvicorn apps.api.main:app --reload
```

Then start the Next.js page:

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

Open <http://127.0.0.1:3000>. See the complete demo, screenshot, acceptance
evidence, and retrospective in [docs/milestone-v0.1.md](docs/milestone-v0.1.md).

Production-boundary endpoints:

```text
POST   /assets
GET    /assets
POST   /assets/{asset_id}/readings
POST   /assets/{asset_id}/readings/batch
POST   /optimizations/sga
GET    /optimizations
GET    /optimizations/{run_id}
POST   /briefs
GET    /briefs
```

List endpoints use bounded pagination. `GET /assets` accepts `offset`, `limit`,
`symbol`, and `currency`; the readings endpoint accepts `offset`, `limit`,
`observed_from`, and `observed_to`. Time boundaries are inclusive.

SGA uses aligned PriceReadings in the requested inclusive date range. At least
three aligned prices are required. Each result records its parameters, seed,
fitness, convergence generation, runtime, metrics, and per-asset allocations.

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
- modularize AGA using the same optimization boundary;
- add backtesting and evaluation;
- expose an optimization API endpoint;
- add deployment configuration after the API contract stabilizes.
