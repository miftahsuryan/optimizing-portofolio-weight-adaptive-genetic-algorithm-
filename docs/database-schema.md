# Core database schema

The SQLAlchemy models in `src/portfolio_optimization/repositories/models.py`
are the application metadata source. Alembic imports that metadata for schema
comparison, while committed revisions remain the only mechanism used to change
a deployed database.

## Tables and integrity rules

| Table | Important keys and constraints | Indexes |
| --- | --- | --- |
| `assets` | UUID PK; unique uppercase `symbol`; uppercase `currency`; all columns required | unique index backing `symbol` |
| `price_readings` | UUID PK; `asset_id` FK to `assets` with cascade delete; positive `close`; unique `(asset_id, observed_at)`; all columns required | `(asset_id, observed_at)` for time-series reads |
| `optimization_runs` | UUID PK; `start_date <= end_date`; all result, parameter, and audit columns required | primary key |
| `allocations` | UUID PK; run FK cascades on delete; asset FK restricts delete; weight in `[0, 1]`; unique `(optimization_run_id, asset_id)`; all columns required | unique composite index backing the allocation key |
| `portfolio_briefs` | UUID PK; risk profile limited to `conservative`, `balanced`, or `growth`; all columns required | `created_at` |

Foreign-key indexes are intentional rather than automatic. The composite
price-reading index supports the main asset/time query. The allocation unique
constraint starts with `optimization_run_id`, supporting retrieval by run;
there is no additional asset-only index until an asset-oriented query requires
one.

## Revision chain

1. `20260818_0001` creates assets, price readings, optimization runs, and
   allocations, including their foreign keys, checks, uniqueness, and query
   index.
2. `20260819_0002` creates portfolio briefs and its chronological index.

Apply and inspect the current revision with:

```bash
alembic upgrade head
alembic current
```

Before merging a new revision, verify a clean database can complete the full
round trip:

```bash
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

`tests/test_migrations.py` performs the same lifecycle on a temporary empty
SQLite database in CI. PostgreSQL remains the production dialect and should be
used for the deployment smoke test.
