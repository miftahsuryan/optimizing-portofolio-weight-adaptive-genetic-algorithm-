class PortfolioOptimizationError(Exception):
    """Base exception for expected portfolio domain failures."""

    code = "portfolio_optimization_error"


class ConfigurationError(PortfolioOptimizationError):
    """Raised when application configuration is invalid."""

    code = "configuration_error"


class DataValidationError(PortfolioOptimizationError):
    """Raised when input data fails validation."""

    code = "data_validation_error"
