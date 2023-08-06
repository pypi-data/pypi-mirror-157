"""
Position event.
"""
from ..event.event import Event, EventType
from .position import Position


class PositionEvent(Event):
    """
    Position event directly from live broker.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """
        Initialises order
        """
        self.event_type = EventType.POSITION
        self.full_symbol = ""
        self_sec_type = ""  # pylint: disable=unused-variable
        self.average_cost = 0.0
        self.size = 0
        self.pre_size = 0
        self.freezed_size = 0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.account = ""
        self.timestamp = ""

    def to_position(self):
        """
        To position.
        """
        pos = Position(self.full_symbol, self.average_cost, self.size)
        pos.realized_pnl = self.realized_pnl
        pos.unrealized_pnl = self.unrealized_pnl
        pos.account = self.account

        return pos

    def __str__(self):
        return (
            f"Ticker: {self.full_symbol}, Cost: {self.average_cost}, "
            f"Size: {self.size}, opl: {self.unrealized_pnl}, rpl: {self.realized_pnl}"
        )
