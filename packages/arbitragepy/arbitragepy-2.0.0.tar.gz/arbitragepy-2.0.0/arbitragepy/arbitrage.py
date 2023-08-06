from decimal import Decimal

from arbitragepy.enums import OrderSide
from arbitragepy.exceptions import (
    NotionalLessThanMinNotionalError,
    QuantityLessThanMinQuantityError,
)
from arbitragepy.models import (
    ArbitragePayload,
    ArbitrageResult,
    OrderPayload,
)
from arbitragepy.fee import minus_fee
from arbitragepy.quantity_increment import (
    to_compatible_quantity_increment,
    validate_quantity_increments,
)
from arbitragepy.spread import get_spread


def arbitrage(
    ask: ArbitragePayload,
    bid: ArbitragePayload,
    make_compatible_quantity_increments: bool = True,
) -> ArbitrageResult:
    """Do arbitrage calculations between `ask` and `bid` orders.

    Calculates spread, profit between ask and bid orders including fee.
    Selects min currency quantity from ask and bid orders.

    Checks that quantity great than allowed min quantity.
    Checks that notional value great than allowed min notional value.

    If balances in `ask` and `bid` is not None checks that quantity less than balance.

    Args:
        ask: info about symbol, order and quote currency balance on ask exchange.
        bid: info about symbol, order and base currency balance on bid exchange.
        make_compatible_quantity_increments: if True will be chosen
            max quantity increment from ask and bid
            and check that they are compatible.
            Defaults to True.

    Returns:
        Result of arbitrage.
    """

    ask_price = ask.order.price
    bid_price = bid.order.price
    ask_fee = ask.fee
    bid_fee = bid.fee
    ask_qty_inc = ask.symbol.quantity_increment
    bid_qty_inc = bid.symbol.quantity_increment
    ask_balance = ask.balance
    bid_balance = bid.balance
    ask_fee_in_base_currency = ask.symbol.fee_in_base_currency

    if make_compatible_quantity_increments:
        validate_quantity_increments(ask_qty_inc, bid_qty_inc)
        ask_qty_inc = bid_qty_inc = max(ask_qty_inc, bid_qty_inc)

    # Select lowest order quantity among ask, bid orders and max quantity limit
    ask_quantity = bid_quantity = min(
        ask.order.quantity,
        bid.order.quantity,
        ask.symbol.max_quantity,
        bid.symbol.max_quantity,
    )
    ask_quantity = to_compatible_quantity_increment(ask_quantity, ask_qty_inc)
    bid_quantity = to_compatible_quantity_increment(bid_quantity, bid_qty_inc)

    if ask_balance is not None and bid_balance is not None:
        if not ask_fee_in_base_currency:
            ask_balance = minus_fee(ask_balance, ask_fee)

        # Select lowest quantity among max available quantity and order quantity on ask exchange
        max_ask_quantity = to_compatible_quantity_increment(
            ask_balance / ask_price, ask_qty_inc
        )
        ask_quantity = min(ask_quantity, max_ask_quantity)
        ask_quantity = to_compatible_quantity_increment(ask_quantity, ask_qty_inc)

        # Select lowest quantity among max available quantity and order quantity on bid exchange
        bid_quantity = min(bid_quantity, bid_balance)
        bid_quantity = to_compatible_quantity_increment(bid_quantity, bid_qty_inc)

        ask_quantity = bid_quantity = min(ask_quantity, bid_quantity)
        bid_quantity = to_compatible_quantity_increment(bid_quantity, bid_qty_inc)
        ask_quantity = to_compatible_quantity_increment(ask_quantity, ask_qty_inc)

    ask_notional_value = ask_quantity * ask_price

    if ask_fee_in_base_currency:
        ask_taken_fee = ask_quantity * ask_fee / 100
        ask_quantity_with_fee = ask_quantity - ask_taken_fee
        bid_quantity = to_compatible_quantity_increment(
            ask_quantity_with_fee, bid_qty_inc
        )
    else:
        ask_taken_fee = ask_notional_value * ask_fee / 100
        ask_notional_value += ask_taken_fee

    bid_notional_value = bid_quantity * bid_price
    bid_taken_fee = bid_notional_value * bid_fee / 100
    bid_notional_value -= bid_taken_fee

    check_quantity_great_than_min_quantity(
        side=OrderSide.BID, quantity=bid_quantity, min_quantity=bid.symbol.min_quantity
    )
    check_notional_great_than_min_notional(
        side=OrderSide.BID,
        notional=bid_notional_value,
        min_notional=bid.symbol.min_notional,
    )

    check_quantity_great_than_min_quantity(
        side=OrderSide.ASK, quantity=ask_quantity, min_quantity=ask.symbol.min_quantity
    )
    check_notional_great_than_min_notional(
        side=OrderSide.ASK,
        notional=ask_notional_value,
        min_notional=ask.symbol.min_notional,
    )

    ask_order = OrderPayload(
        price=ask_price,
        quantity=ask_quantity,
        notional_value=ask_notional_value,
        taken_fee=ask_taken_fee,
        fee_in_base_currency=ask_fee_in_base_currency,
    )
    bid_order = OrderPayload(
        price=bid_price,
        quantity=bid_quantity,
        notional_value=bid_notional_value,
        taken_fee=bid_taken_fee,
        fee_in_base_currency=False,
    )
    spread = get_spread(ask_notional_value, bid_notional_value)
    profit = bid_notional_value - ask_notional_value

    return ArbitrageResult(
        ask_order=ask_order, bid_order=bid_order, spread=spread, profit=profit
    )


def check_quantity_great_than_min_quantity(
    side: OrderSide, quantity: Decimal, min_quantity: Decimal
) -> None:
    """Raises :exc:`QuantityLessThanMinQuantityError` if `quantity` less than `min_quantity`."""

    if quantity < min_quantity:
        raise QuantityLessThanMinQuantityError(
            side=side, quantity=quantity, min_quantity=min_quantity
        )


def check_notional_great_than_min_notional(
    side: OrderSide, notional: Decimal, min_notional: Decimal
) -> None:
    """Raises :exc:`NotionalLessThanMinNotionalError` if `notional` less than `min_notional`."""

    if notional < min_notional:
        raise NotionalLessThanMinNotionalError(
            side=side, notional=notional, min_notional=min_notional
        )
