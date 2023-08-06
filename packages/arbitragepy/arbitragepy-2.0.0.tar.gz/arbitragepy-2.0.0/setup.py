# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arbitragepy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'arbitragepy',
    'version': '2.0.0',
    'description': 'Arbitrage utilities. Has functions that make it easy to work with arbitrage mathematics.',
    'long_description': '# arbitragepy - the simple arbitrage calculations package\n\nYou can easily calculate arbitrage situation between 2 exchanges.\n\nDoesn\'t use `float` in calculations, only `Decimal` from `decimal` python standard library package, which guarantees accurate calculations with high precision.\n\n## Installation\n\n```shell\npoetry add arbitragepy\n```\n\nor\n\n```shell\npip install arbitragepy\n```\n\n## Documentation\n\n### Quick Start\n\n```python\nfrom decimal import Decimal\n\nfrom arbitragepy import (\n    arbitrage,\n    SymbolInfo,\n    OrderInfo,\n    OrderPayload,\n    ArbitragePayload,\n    ArbitrageResult,\n)\n\n\nask_payload = ArbitragePayload(\n    symbol=SymbolInfo(quantity_increment=Decimal("0.01")),\n    order=OrderInfo(price=Decimal("10.5"), quantity=Decimal("100.15")),\n    balance=Decimal("200"),\n    fee=Decimal("0.1")\n)\nbid_payload = ArbitragePayload(\n    symbol=SymbolInfo(quantity_increment=Decimal("0.01")),\n    order=OrderInfo(price=Decimal("11.5"), quantity=Decimal("50.3")),\n    balance=Decimal("65"),\n    fee=Decimal("0.1")\n)\n\nresult = arbitrage(ask=ask_payload, bid=bid_payload)\n\nassert result == ArbitrageResult(\n    ask_order=OrderPayload(\n        price=Decimal("10.5"),\n        quantity=Decimal("19.02"),\n        notional_value=Decimal("199.90971"),\n        taken_fee=Decimal("0.19971"),\n        fee_in_base_currency=False,\n    ),\n    bid_order=OrderPayload(\n        price=Decimal("11.5"),\n        quantity=Decimal("19.02"),\n        notional_value=Decimal("218.51127"),\n        taken_fee=Decimal("0.21873"),\n        fee_in_base_currency=False,\n    ),\n    spread=Decimal("9.304980733552162123590695000"),\n    profit=Decimal("18.60156"),\n)\n```\n',
    'author': 'astsu',
    'author_email': 'astsu.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/astsu-dev/arbitragepy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
