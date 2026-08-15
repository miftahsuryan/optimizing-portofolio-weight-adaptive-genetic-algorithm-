# IDX30 Portfolio Optimization

A modular Python project for preparing IDX30 stock-price data and developing a
portfolio-weight optimization workflow. The repository is being refactored from
a research notebook into reusable modules that can be called from a command-line
interface (CLI), a FastAPI application, tests, and future web clients.

## Current capabilities

The current application can:

- load and validate daily closing-price data from CSV;
- load an IDX30 constituent matrix covering multiple evaluation periods;
- find the intersection of tickers present in every constituent period;
- filter the price dataset to consistently listed IDX30 stocks;
- calculate daily returns independently for each ticker;
- calculate mean returns and a return covariance matrix;
- print a concise dataset and statistics summary through the CLI;
- expose a FastAPI health endpoint;
- verify the workflow with automated tests.

Portfolio optimization with the Standard Genetic Algorithm (SGA) and Adaptive
Genetic Algorithm (AGA) remains planned work. The current FastAPI application
only exposes a health endpoint; it does not expose an optimization endpoint yet.

## Processing workflow

```text
IDX30 constituent matrix
        |
        v
Find ticker intersection across all periods
        |
        v
Daily closing-price CSV --> validate and normalize types
        |                           |
        +---------------------------+
                    |
                    v
Filter prices to consistent IDX30 tickers
                    |
                    v
Calculate daily returns per ticker
                    |
                    v
Mean returns + covariance matrix
                    |
             +------+------+
             |             |
             v             v
            CLI       Future model/API
```

With the currently configured research data, the intersection covers 13 IDX30
constituent periods and produces 22 consistently listed tickers.

## Project structure

```text
.
├── apps/
│   ├── api/                         # FastAPI application
│   └── web/                         # Reserved for a future web client
├── data/                            # Research price and constituent data
├── notebook_raw/                    # Original research notebook
├── src/portfolio_optimization/
│   ├── compute_statistic/           # Returns, means, and covariance
│   ├── ingestion/                   # CSV loading and validation
│   ├── preprocessing/               # IDX30 intersection and filtering
│   ├── services/                    # Application-level services
│   ├── cli.py                       # CLI orchestration
│   ├── config.py                    # Environment-based configuration
│   └── exceptions.py                # Application-specific exceptions
├── tests/                           # Automated tests and small fixtures
├── .env.example                     # Example environment configuration
└── pyproject.toml                   # Package, dependency, and test settings
```

## Requirements

- Python 3.12 or newer
- `pip`
- A virtual environment is strongly recommended

Runtime dependencies:

- pandas
- FastAPI
- Uvicorn

Development dependencies:

- pytest
- HTTPX

All dependency declarations are maintained in `pyproject.toml`.

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/miftahsuryan/optimizing-portofolio-weight-adaptive-genetic-algorithm-.git
cd optimizing-portofolio-weight-adaptive-genetic-algorithm-
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project in editable mode with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Editable installation makes imports resolve to the current files under `src/`,
so normal source-code changes do not require reinstalling the package.

## Configuration

The application reads two optional environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `PRICE_DATA_PATH` | Daily closing-price CSV | `data/idx30_close_prices_daily_2023-2026_raw.csv` |
| `IDX30_CONSTITUENTS_PATH` | IDX30 constituent-period matrix | `data/List_IDX30_Lengkap_2022_2026.xlsx - Matriks 2022-2026.csv` |

To use different files for one command:

```bash
PRICE_DATA_PATH="path/to/prices.csv" \
IDX30_CONSTITUENTS_PATH="path/to/constituents.csv" \
python -m portfolio_optimization
```

The price CSV must contain these columns:

```text
Date,ticker,Close
```

The constituent CSV must contain one column per evaluation period. An optional
`No` column is treated as a row identifier and excluded from the intersection.

## Run the CLI

With the virtual environment active:

```bash
python -m portfolio_optimization
```

Without activating it:

```bash
.venv/bin/python -m portfolio_optimization
```

Example output using the current research data:

```text
Consistent IDX30 Dataset Summary
Periods     : 13
Rows        : 16038
Tickers     : 22
Start date  : 2022-12-30
End date    : 2026-01-26
Missing     : 0
Portfolio Statistics
Return rows : 728
Assets      : 22
Covariance  : 22 x 22
```

## Run the FastAPI application

Start the development server:

```bash
uvicorn apps.api.main:app --reload
```

Available URLs:

- Health endpoint: <http://127.0.0.1:8000/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

The health response is:

```json
{"status": "ok"}
```

The `--reload` option is intended for local development and should not be used
as the production deployment configuration.

## Run tests

Run the complete test suite:

```bash
pytest -q
```

Or explicitly use the project environment:

```bash
.venv/bin/pytest -q
```

Run only the API health test:

```bash
pytest -q tests/test_api_health.py
```

Run only the IDX30 intersection tests:

```bash
pytest -q tests/test_idx30_intersection.py
```

Tests use small fixtures under `tests/fixtures/` rather than the full research
dataset, making them deterministic and fast.

## Module responsibilities

### Ingestion

`ingestion/load_prices.py` validates the price file, required columns, dates,
numeric closing prices, and positive price values.

`ingestion/load_constituents.py` loads and validates the constituent-period
matrix.

### Preprocessing

`preprocessing/idx30_intersection.py` converts each period column into a ticker
set, finds the intersection across all periods, and filters the price data to
the selected tickers.

### Portfolio statistics

`compute_statistic/portfolio_statistics.py` calculates daily returns per ticker,
mean returns, and the covariance matrix used as inputs to future portfolio
optimization algorithms.

### Interfaces

`cli.py` orchestrates the current data pipeline and prints its summary.

`apps/api/main.py` creates the FastAPI application and exposes `GET /health`.
Core calculations should remain under `src/portfolio_optimization/` so the CLI,
API, notebook, and future web application can reuse the same implementation.

## Planned development

- complete preprocessing policies for missing values, duplicates, and research
  date ranges;
- add train, validation, and test period splitting;
- implement portfolio fitness and constraints;
- modularize SGA and AGA from the research notebook;
- add optimization evaluation and backtesting;
- create an optimization service shared by the CLI and API;
- expose a validated `POST /optimize` endpoint;
- add deployment configuration after the API contract is stable.

## Development principle

The notebook remains useful for exploration and research analysis. Stable and
reusable calculations belong in the package under `src/`, where they can be
tested and shared by every application interface.
