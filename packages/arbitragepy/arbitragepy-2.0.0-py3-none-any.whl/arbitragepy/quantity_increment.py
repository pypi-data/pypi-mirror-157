from decimal import Decimal

from arbitragepy.exceptions import ImcompabileQuantityIncrementsError


def is_compatible_quantity_increments(
    ask_qty_inc: Decimal, bid_qty_inc: Decimal
) -> bool:
    """Returns True if `ask_qty_inc` divided by `bid_qty_inc` or `bid_qty_inc` divided by `ask_qty_inc`.

    Args:
        ask_qty_inc (Decimal)
        bid_qty_inc (Decimal)

    Returns:
        bool
    """

    return ask_qty_inc % bid_qty_inc == 0 or bid_qty_inc % ask_qty_inc == 0


def to_compatible_quantity_increment(n: Decimal, qty_inc: Decimal) -> Decimal:
    """Converts `n` to number which divided on `qty_inc`.

    Args:
        n (Decimal)
        qty_inc (Decimal): quantity increment

    Returns:
        Decimal
    """

    return n // qty_inc * qty_inc


def validate_quantity_increments(ask_qty_inc: Decimal, bid_qty_inc: Decimal) -> None:
    """Validates quantity increments.

    Raises ImcompabileQuantityIncrementsError if quantity increments are imcompatible, otherwise do nothing.

    Args:
        ask_qty_inc (Decimal)
        bid_qty_inc (Decimal)

    Raises:
        ImcompabileQuantityIncrementsError: will be raised if qunatity incrementes is imcompatible.
    """

    if not is_compatible_quantity_increments(ask_qty_inc, bid_qty_inc):
        raise ImcompabileQuantityIncrementsError(ask_qty_inc, bid_qty_inc)
