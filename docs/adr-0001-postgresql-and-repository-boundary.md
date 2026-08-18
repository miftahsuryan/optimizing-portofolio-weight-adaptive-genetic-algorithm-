# ADR 0001: PostgreSQL behind repository boundaries

- Status: Accepted
- Date: 2026-08-18

## Context

The domain and application services must remain independently testable while
production data needs transactional persistence, constraints, and migrations.

## Decision

PostgreSQL is the production database. SQLAlchemy owns engine/session lifecycle
and Alembic owns schema migrations. Application services depend only on the
repository protocols in `repositories/protocols.py`; they do not receive ORM
models or SQLAlchemy sessions. In-memory implementations remain the default
composition until PostgreSQL repository adapters are introduced.

`DATABASE_URL` is environment-driven. A session commits after a successful unit
of work and rolls back on errors. `/health/db` runs `SELECT 1` so deployment
checks verify a real database round trip; `/health` remains a process liveness
check and deliberately does not depend on PostgreSQL.

## Consequences

- Unit and API contract tests stay fast and deterministic with dependency
  overrides.
- Database integration tests can use the same production engine/session setup.
- A deployment must run `alembic upgrade head` before serving traffic.
- Implementing PostgreSQL repository adapters is a separate change and cannot
  leak persistence concerns into domain services.
