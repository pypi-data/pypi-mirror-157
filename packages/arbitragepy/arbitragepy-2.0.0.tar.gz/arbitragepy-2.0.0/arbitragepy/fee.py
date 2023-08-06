from decimal import Decimal


def plus_fee(n: Decimal, fee: Decimal) -> Decimal:
    """Returns the number from which, if you subtract the `fee` percent, you get `n`.

    Args:
        n (Decimal)
        fee (Decimal): fee in percent which greater than 0

    Returns:
        Decimal
    """

    return n / (1 - fee / 100)


def minus_fee(n: Decimal, fee: Decimal) -> Decimal:
    """Returns the number to which, if you add the `fee` percent, you get `n`.

    Args:
        n (Decimal)
        fee (Decimal): fee in percent which greater than 0

    Returns:
        Decimal
    """

    return n / (1 + fee / 100)
