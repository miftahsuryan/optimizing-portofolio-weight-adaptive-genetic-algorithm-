class PortfolioOptimizationError(Exception):
    """Base exception for the portfolio optimization application"""

class ConfigurationError(PortfolioOptimizationError):
    """"Raised when application Configuration is invalid"""

class DataValidationError(PortfolioOptimizationError):
    """Raised when input data fails validation"""