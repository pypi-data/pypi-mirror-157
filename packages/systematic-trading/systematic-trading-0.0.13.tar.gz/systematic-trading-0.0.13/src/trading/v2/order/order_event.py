"""
Order event.
"""
from .order_status import OrderStatus
from .order_flag import OrderFlag
from .order_type import OrderType
from ..event.event import Event, EventType


class OrderEvent(Event):
    """
    Order event
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """
        Order and order status.
        """
        self.event_type = EventType.ORDER
        self.order_id = -1
        self.order_type = OrderType.MARKET
        self.order_flag = OrderFlag.OPEN
        self.order_status = OrderStatus.UNKNOWN
        self.full_symbol = ""
        self.order_size = 0  # short < 0, long > 0
        self.limit_price = 0.0
        self.stop_price = 0.0
        self.fill_size = 0
        self.fill_price = 0.0
        self.create_time = None
        self.fill_time = None
        self.cancel_time = None
        self.account = ""
        self.source = -1  # sid, -1: unknown, 0: discretionary
        self.timestamp = ""

    def __str__(self):
        return (
            f"Time: {self.timestamp}, Source: {self.source}, "
            f"Type: {self.order_type}, LMT: {self.limit_price}, "
            f"STP {self.stop_price} Size {self.order_size}"
        )
