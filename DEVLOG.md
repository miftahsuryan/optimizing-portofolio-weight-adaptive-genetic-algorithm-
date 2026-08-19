# Development Log

A chronological summary of the project's development.

## 2026-08-13 — Initial prototype

- Added the research notebook and raw IDX30 price data.
- Implemented and tested the first daily-return calculation.

## 2026-08-14 — Package foundation

- Corrected validation messages for invalid prices.
- Added the early `portfolio_optimization` package.
- Added initial configuration, CSV loading, and application entry points.

## 2026-08-15 — Data workflow and API foundation

- Converted the project to an installable `src`-layout package.
- Added environment configuration, CSV validation, summary service, CLI, and
  automated tests.
- Added end-to-end tests for the command-line workflow.
- Fixed the test package path.
- Added the FastAPI application and `GET /health`.
- Added API health tests.
- Added price ingestion, IDX30 constituent filtering, and portfolio statistics.
- Added supporting configuration, CLI behavior, fixtures, and tests.
- Added setup, usage, architecture, and testing instructions to the README.

## 2026-08-16 — General analysis API

- Added the typed `GET /portfolio/analysis` API.
- Made the core workflow market-neutral instead of IDX30-specific.
- Removed tracked market-specific datasets and updated related tests.

## 2026-08-17 — Domain services and SGA

- Added Asset, PriceReading, OptimizationRun, and Allocation entities.
- Added repository interfaces and in-memory implementations.
- Added asset, price-reading, and optimization services and API routes.
- Added the Standard Genetic Algorithm implementation.
- Added the ERD, project-structure documentation, and complete test coverage for
  the new boundaries.

## 2026-08-18 — API tests and database setup

- Added pagination and filtering for Assets and PriceReadings.
- Added PostgreSQL configuration, SQLAlchemy engine/session management, and
- Added the initial Alembic migration.
- Added an ADR and HTTP API collection.
- Added production API behavior and database smoke tests.

## 2026-08-19 — Milestone v0.1 vertical slice

- Added a Next.js page with typed fetch calls and explicit component state.
- Added the persisted PortfolioBrief API and PostgreSQL migration.
- Added deterministic risk-profile AI-stub responses.
- Verified fresh-client persistence, the complete Python suite, production web
  build, dependency audit, and captured the milestone screenshot.
- Documented demo steps, acceptance evidence, and the retrospective.
