from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SymbolInfo:
    """Info about symbol.

    Args:
        quantity_increment: step size for currency quantity in order.
        min_quantity: min quantity of currency in order. Defaults to 0.
        max_quantity: max quantity of currency in order. Defaults to infinity.
        min_notional: min value of quantity * price. Defaults to 0.
        fee_in_base_currency: True if fee after purchase
            will be taken in the base currency. Defaults to False.
    """

    quantity_increment: Decimal
    min_quantity: Decimal = Decimal(0)
    max_quantity: Decimal = Decimal("inf")
    min_notional: Decimal = Decimal(0)
    fee_in_base_currency: bool = False


@dataclass(frozen=True)
class OrderInfo:
    """Info about order.

    Args:
        price: currency price in order.
        quantity: quantity of currency in order.
    """

    price: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class ArbitragePayload:
    """Info about symbol, order and balance.

    Will be used for arbitrage calculations.

    Args:
        symbol: info about symbol.
        order: info about order.
        balance: if ask exchnage then balance of symbol quote currency.
            If bid exchange then balance of symbol base currency.
        fee: fee in percent. Defaults to 0.
    """

    symbol: SymbolInfo
    order: OrderInfo
    balance: Decimal | None = None
    fee: Decimal = Decimal(0)


@dataclass(frozen=True)
class OrderPayload:
    """Data for placing order on exchange.

    Args:
        price: currency price in order.
        quantity: quantity of currency in order.
        notional_value: value of `quantity * price`.
        taken_fee: fee that will be taken.
        fee_in_base_currency: True if fee after purchase
            will be taken in the base currency.
    """

    price: Decimal
    quantity: Decimal
    notional_value: Decimal
    taken_fee: Decimal
    fee_in_base_currency: bool


@dataclass(frozen=True)
class ArbitrageResult:
    """Result of arbitrage calculations.

    Args:
        ask_order: data for placing order on ask exchange.
        bid_order: data for placing order on bid exchange.
        spread: clear spread in percent between ask and bid prices.
        profit: clear profit
    """

    ask_order: OrderPayload
    bid_order: OrderPayload
    spread: Decimal
    profit: Decimal
