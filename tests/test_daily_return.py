import pytest

from portfolio_optimization.compute_statistic.daily_return import (
    calculate_daily_return
)

def test_daily_return_increases() -> None:
    # Arrange
    current_price = 1000.0
    previous_price = 950.0
    result = (1000.0 - 950.0) / 950.0

    # Act
    test_result = calculate_daily_return(current_price, previous_price)

    # Assert
    assert test_result == pytest.approx(result)


def test_daily_return_decreases() -> None:
    # Arrange
    current_price = 1000
    previous_price = 1050
    result = (1000 - 1050) / 1050

    # Act
    test_result = calculate_daily_return(current_price, previous_price)

    # Assert
    assert test_result == pytest.approx(result)

def test_daily_return_with_wrong_or_invalid_input() -> None:

    with pytest.raises(TypeError):
        calculate_daily_return(
            current_price = '1000',
            previous_price = '1050'
        )

def test_daily_return_with_current_price_non_positive() -> None:

    with pytest.raises(ValueError):
        calculate_daily_return(
        current_price = 0.0,
        previous_price = 1050.0 
        )

    with pytest.raises(ValueError):
        calculate_daily_return(
        current_price = -1000.0,
        previous_price = 1050.0 
        )


def test_daily_return_with_previous_price_non_positive() -> None:

    with pytest.raises(ValueError):
        calculate_daily_return(
        current_price = 1000.0,
        previous_price = 0.0 
        )

    with pytest.raises(ValueError):
        calculate_daily_return(
        current_price = 1000.0,
        previous_price = -1050.0 
        )