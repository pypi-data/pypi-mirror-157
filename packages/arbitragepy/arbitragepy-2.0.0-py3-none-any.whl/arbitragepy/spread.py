from decimal import Decimal


def get_spread(ask_price: Decimal, bid_price: Decimal) -> Decimal:
    """Returns spread in percent between `ask_price` and `bid_price` prices.

    Args:
        ask_price (Decimal): price for buy
        bid_price (Decimal): price for sell

    Returns:
        Decimal
    """

    return (bid_price / ask_price - 1) * 100
