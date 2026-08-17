# Project structure

The repository separates deployable applications, reusable business code,
research artifacts, documentation, local data, and tests.

```text
apps/api/                         FastAPI delivery layer
  routers/                        HTTP routes grouped by resource
  schemas/                        Request and response models by resource
src/portfolio_optimization/       Reusable installed Python package
  analytics/                      Return and covariance calculations
  domain/                         Entities and domain invariants
  ingestion/                      External data loading and validation
  optimization/                   Pure optimization algorithms
  repositories/                   Persistence contracts and implementations
  services/                       Application use cases and transactions
docs/                             Architecture documentation
notebooks/                        Research and exploratory notebooks
data/                             Local datasets ignored by Git
tests/                            Automated tests and small committed fixtures
```

## Naming rules

- Python packages and modules use lowercase `snake_case`.
- Resource modules use plural nouns when they contain a group of related
  definitions, such as `assets.py` and `optimizations.py`.
- Service modules retain the `_service` suffix because it distinguishes use
  cases from similarly named domain and API modules in search results.
- Algorithm modules use the algorithm name, such as `sga.py`.
- Test modules mirror the behavior under test and start with `test_`.
- Research notebooks use descriptive lowercase names and do not define runtime
  application behavior.

The `domain` and `apps.api.schemas` package initializers provide stable import
facades. Internal files can therefore be reorganized without forcing callers
to depend on their exact locations.
