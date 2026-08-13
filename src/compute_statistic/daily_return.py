def calculate_daily_return(
    current_price: float,
    previous_price: float,
) -> float:
    """Calculate the simple daily return between two closing prices.

    Args:
        current_price: Closing price on the current observation day.
        previous_price: Closing price on the previous observation day.

    Returns:
        Daily simple return expressed as a decimal.

    Raises:
        ValueError: If current_price or previous_price is not positive.
    """
    # 1. Cek tipe data terlebih dahulu (pastikan int atau float)
    if not isinstance(current_price, (int, float)) or not isinstance(
        previous_price, (int, float)
    ):
        raise TypeError("The data tpe should be float or int")
        
    if current_price <= 0.0:
        raise ValueError("Current price must be greater than zero.")

    if previous_price <= 0.0:
        raise ValueError("Current price must be greater than zero.")

    daily_return = (current_price - previous_price) / previous_price

    return daily_return 