"""
Fill event.
"""
from ..event.event import Event, EventType
from ..position.position import Position


class FillEvent(Event):
    """
    Fill event, with filled quantity/size and price
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """
        Initialises fill
        """
        self.event_type = EventType.FILL
        self.order_id = -1
        self.fill_id = -1
        self.full_symbol = ""
        self.fill_time = ""
        self.fill_price = 0.0
        self.fill_size = 0  # size < 0 means short order is filled
        self.exchange = ""
        self.commission = 0.0
        self.account = ""
        self.source = -1
        self.api = ""

    def to_position(self, multiplier: int = 1):
        """
        if there is no existing position for this symbol, this fill will create a new position
        (otherwise it will be adjusted to exisitng position)

        Parameters
        ----------
            multiplier : int
                Multiplier for position size.
        """
        if self.fill_size > 0:
            average_price_including_commission = (
                self.fill_price + self.commission / multiplier
            )
        else:
            average_price_including_commission = (
                self.fill_price - self.commission / multiplier
            )

        new_position = Position(
            self.full_symbol, average_price_including_commission, self.fill_size
        )
        return new_position

    def __str__(self):
        return (
            f"Time: {self.fill_time}, Source: {self.source}, "
            f"Oid: {self.order_id}, Ticker: {self.full_symbol}, "
            f"Price: {self.fill_price}, Size {self.fill_size} Comm {self.commission}"
        )
