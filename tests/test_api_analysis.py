from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.main import app
from portfolio_optimization.config import AppConfig
from portfolio_optimization.exceptions import ConfigurationError


client = TestClient(app, raise_server_exceptions=False)


def test_portfolio_analysis_uses_response_schema(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.api.main.load_config",
        lambda: AppConfig(
            price_data_path=Path("tests/fixtures/prices_valid.csv"),
        ),
    )

    response = client.get("/portfolio/analysis")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == {
        "rows": 6,
        "tickers": 2,
        "start_date": "2025-01-02",
        "end_date": "2025-01-06",
        "missing_close": 0,
    }
    assert set(body["statistics"]["mean_returns"]) == {"AAA", "BBB"}
    assert set(body["statistics"]["covariance_matrix"]) == {"AAA", "BBB"}


def test_portfolio_analysis_returns_consistent_domain_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.api.main.load_config",
        lambda: AppConfig(
            price_data_path=Path("tests/fixtures/prices_missing_column.csv"),
        ),
    )

    response = client.get("/portfolio/analysis")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "data_validation_error",
            "message": "Missing required columns: ['Close']",
        },
    }


def test_portfolio_analysis_returns_consistent_configuration_error(
    monkeypatch,
) -> None:
    def invalid_config():
        raise ConfigurationError("Invalid application configuration.")

    monkeypatch.setattr("apps.api.main.load_config", invalid_config)

    response = client.get("/portfolio/analysis")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "configuration_error",
            "message": "Invalid application configuration.",
        },
    }


def test_portfolio_analysis_returns_consistent_missing_file_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.csv"
    monkeypatch.setattr(
        "apps.api.main.load_config",
        lambda: AppConfig(price_data_path=missing_file),
    )

    response = client.get("/portfolio/analysis")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "data_file_not_found",
            "message": f"Price data file not found: {missing_file}",
        },
    }


def test_openapi_documents_analysis_success_and_error_schemas() -> None:
    operation = client.get("/openapi.json").json()["paths"][
        "/portfolio/analysis"
    ]["get"]

    assert operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("/PortfolioAnalysisResponse")
    assert operation["responses"]["422"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("/ErrorResponse")
