import enum


class OrderSide(str, enum.Enum):
    """Exchange order side."""

    ASK = "ASK"
    BID = "BID"
