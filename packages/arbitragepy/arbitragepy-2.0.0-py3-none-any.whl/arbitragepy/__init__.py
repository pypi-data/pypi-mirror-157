from arbitragepy.arbitrage import arbitrage
from arbitragepy.exceptions import (
    ImcompabileQuantityIncrementsError,
    NotionalLessThanMinNotionalError,
    QuantityLessThanMinQuantityError,
)
from arbitragepy.fee import minus_fee, plus_fee
from arbitragepy.models import (
    ArbitragePayload,
    ArbitrageResult,
    SymbolInfo,
    OrderInfo,
    OrderPayload,
)
from arbitragepy.quantity_increment import (
    is_compatible_quantity_increments,
    to_compatible_quantity_increment,
    validate_quantity_increments,
)
from arbitragepy.spread import get_spread


__all__ = [
    "arbitrage",
    "minus_fee",
    "plus_fee",
    "ArbitragePayload",
    "ArbitrageResult",
    "SymbolInfo",
    "OrderInfo",
    "OrderPayload",
    "ImcompabileQuantityIncrementsError",
    "NotionalLessThanMinNotionalError",
    "QuantityLessThanMinQuantityError",
    "is_compatible_quantity_increments",
    "to_compatible_quantity_increment",
    "validate_quantity_increments",
    "get_spread",
]
__version__ = "2.0.0"
