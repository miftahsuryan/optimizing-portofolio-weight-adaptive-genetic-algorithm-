class PortfolioOptimizationError(Exception):
    """Base exception for expected portfolio domain failures."""

    code = "portfolio_optimization_error"


class ConfigurationError(PortfolioOptimizationError):
    """Raised when application configuration is invalid."""

    code = "configuration_error"


class DataValidationError(PortfolioOptimizationError):
    """Raised when input data fails validation."""

    code = "data_validation_error"


class DomainValidationError(PortfolioOptimizationError):
    """Raised when a domain entity violates an invariant."""

    code = "domain_validation_error"


class EntityNotFoundError(PortfolioOptimizationError):
    """Raised when a requested domain entity does not exist."""

    code = "entity_not_found"


class DuplicateEntityError(PortfolioOptimizationError):
    """Raised when a domain entity violates a uniqueness rule."""

    code = "duplicate_entity"