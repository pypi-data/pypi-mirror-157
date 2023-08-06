"""
Tick event module.
"""
from datetime import datetime
from enum import Enum

from pandas import Timestamp

from ..event.event import Event, EventType


class TickType(Enum):
    """
    Unlike IB, it does not have tick_size, e.g., TickTypeEnum.BID_SIZE
    """

    TRADE = 0
    BID = 1
    ASK = 2
    FULL = 3


class TickEvent(Event):
    """
    Tick event
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """
        Initialises Tick
        """
        self.event_type = EventType.TICK
        self.tick_type = TickType.TRADE
        self.timestamp = Timestamp("1970-01-01", tz="UTC")
        self.full_symbol = ""
        self.price = 0.0
        self.size = 0
        self.depth = 1
        self.bid_price_L1 = 0.0  # pylint: disable=invalid-name
        self.bid_size_L1 = 0  # pylint: disable=invalid-name
        self.ask_price_L1 = 0.0  # pylint: disable=invalid-name
        self.ask_size_L1 = 0  # pylint: disable=invalid-name
        self.open_interest = 0
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.pre_close = 0.0
        self.upper_limit_price = 0.0
        self.lower_limit_price = 0.0

    def __str__(self):
        return (
            f'{self.timestamp.strftime("%H:%M:%S.%f")},'
            f'{datetime.now().strftime("%H:%M:%S.%f")},{self.full_symbol},'
            f"{self.tick_type},{self.bid_size_L1},{self.bid_price_L1},"
            f"{self.ask_price_L1},{self.ask_size_L1},{self.price},{self.size}"
        )
