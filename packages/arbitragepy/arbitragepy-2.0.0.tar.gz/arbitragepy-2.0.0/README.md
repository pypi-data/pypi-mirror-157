# arbitragepy - the simple arbitrage calculations package

You can easily calculate arbitrage situation between 2 exchanges.

Doesn't use `float` in calculations, only `Decimal` from `decimal` python standard library package, which guarantees accurate calculations with high precision.

## Installation

```shell
poetry add arbitragepy
```

or

```shell
pip install arbitragepy
```

## Documentation

### Quick Start

```python
from decimal import Decimal

from arbitragepy import (
    arbitrage,
    SymbolInfo,
    OrderInfo,
    OrderPayload,
    ArbitragePayload,
    ArbitrageResult,
)


ask_payload = ArbitragePayload(
    symbol=SymbolInfo(quantity_increment=Decimal("0.01")),
    order=OrderInfo(price=Decimal("10.5"), quantity=Decimal("100.15")),
    balance=Decimal("200"),
    fee=Decimal("0.1")
)
bid_payload = ArbitragePayload(
    symbol=SymbolInfo(quantity_increment=Decimal("0.01")),
    order=OrderInfo(price=Decimal("11.5"), quantity=Decimal("50.3")),
    balance=Decimal("65"),
    fee=Decimal("0.1")
)

result = arbitrage(ask=ask_payload, bid=bid_payload)

assert result == ArbitrageResult(
    ask_order=OrderPayload(
        price=Decimal("10.5"),
        quantity=Decimal("19.02"),
        notional_value=Decimal("199.90971"),
        taken_fee=Decimal("0.19971"),
        fee_in_base_currency=False,
    ),
    bid_order=OrderPayload(
        price=Decimal("11.5"),
        quantity=Decimal("19.02"),
        notional_value=Decimal("218.51127"),
        taken_fee=Decimal("0.21873"),
        fee_in_base_currency=False,
    ),
    spread=Decimal("9.304980733552162123590695000"),
    profit=Decimal("18.60156"),
)
```
