from decimal import Decimal

from arbitragepy.enums import OrderSide


class ImcompabileQuantityIncrementsError(Exception):
    """Will be raised if quantity increments is not divided."""

    def __init__(self, ask_qty_inc: Decimal, bid_qty_inc: Decimal) -> None:
        self.ask_qty_inc = ask_qty_inc
        self.bid_qty_inc = bid_qty_inc

    def __str__(self) -> str:
        return f"{self.ask_qty_inc} quantity increment is not divided on {self.bid_qty_inc} quantity increment."


class QuantityLessThanMinQuantityError(Exception):
    """Will be raised if the symbol base currency quantity in order
    less than allowed the symbol base currency min quantity.
    """

    def __init__(
        self, side: OrderSide, quantity: Decimal, min_quantity: Decimal
    ) -> None:
        self.side = side
        self.quantity = quantity
        self.min_quantity = min_quantity

    def __str__(self) -> str:
        return f"on {self.side.lower()} exchange quantity less than allowed symbol min quantity: {self.quantity} < {self.min_quantity}"


class NotionalLessThanMinNotionalError(Exception):
    """Will be raised if the notional value in order
    less than allowed the symbol min notional value.
    """

    def __init__(
        self, side: OrderSide, notional: Decimal, min_notional: Decimal
    ) -> None:
        self.side = side
        self.notional = notional
        self.min_notional = min_notional

    def __str__(self) -> str:
        return f"on {self.side.lower()} exchange notional less than allowed symbol min notional: {self.notional} < {self.min_notional}"
