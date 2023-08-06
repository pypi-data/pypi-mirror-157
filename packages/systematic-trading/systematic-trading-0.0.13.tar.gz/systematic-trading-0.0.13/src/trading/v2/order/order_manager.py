"""
Order manager
"""
from copy import copy
import logging


from ..data.tick_event import TickEvent
from .order_status import OrderStatus
from ..order.fill_event import FillEvent
from ..order.order_event import OrderEvent

_logger = logging.getLogger(__name__)


class OrderManager:
    """
    Manage/track all the orders
    """

    def __init__(self, name="Global"):
        self.name = name
        self.order_dict = {}  # order_id ==> order
        self.fill_dict = {}  # fill_id ==> fill
        self.standing_order_set = set()  # order_id of standing order for convenience
        self.canceled_order_set = set()  # order_id of canceled orders for convenience

    def reset(self):
        """
        Reset all the orders and fills.
        """
        self.order_dict.clear()
        self.fill_dict.clear()
        self.standing_order_set.clear()
        self.canceled_order_set.clear()

    def on_tick(self, tick_event: TickEvent):
        """
        On tick event, update the order status.
        """

    def on_order_status(self, order_event: OrderEvent):
        """
        On order status change from broker including canceled status.

        Parameters
        ----------
            order_event : OrderEvent
                Order event from broker.
        """
        # there should be no negative order id if order is directly placed without queue.
        if order_event.order_id < 0:
            _logger.error(
                "%s OrderManager received negative orderid %s",
                self.name,
                order_event.order_id,
            )

        if order_event.order_id in self.order_dict:
            if (
                order_event.full_symbol
                != self.order_dict[order_event.order_id].full_symbol
            ):
                _logger.error("%s OrderManager Error: orders dont match", self.name)
                return False
            # only change status when it is logical
            if (
                self.order_dict[order_event.order_id].order_status.value
                <= order_event.order_status.value
            ):
                self.order_dict[
                    order_event.order_id
                ].order_status = order_event.order_status
                if order_event.order_status < OrderStatus.FILLED:
                    self.standing_order_set.add(order_event.order_id)
                elif order_event.order_status == OrderStatus.CANCELED:
                    self.canceled_order_set.add(order_event.order_id)
                    self.order_dict[
                        order_event.order_id
                    ].cancel_time = order_event.cancel_time
                    if order_event.order_id in self.standing_order_set:
                        self.standing_order_set.remove(order_event.order_id)
                return True
            # no need to change status
            return False
        # order_id not yet assigned, open order at connection or placed by trader?
        self.order_dict[order_event.order_id] = copy(
            order_event
        )  # it is important to use copy
        if order_event.order_status < OrderStatus.FILLED:
            self.standing_order_set.add(order_event.order_id)
        elif order_event.order_status == OrderStatus.CANCELED:
            self.canceled_order_set.add(order_event.order_id)
            if order_event.order_id in self.standing_order_set:
                self.standing_order_set.remove(order_event.order_id)
        return True

    def on_cancel(self, oid: int):
        """
        This proactively set order status to PENDING_CANCEL

        Parameters
        ----------
            oid : int
                order id
        """
        # Cancel will be handled in order_status
        # self.canceled_order_set.add(oid)
        # if oid in self.standing_order_set:
        #     self.standing_order_set.remove(oid)
        if oid in self.order_dict:
            self.order_dict[oid].order_status = OrderStatus.PENDING_CANCEL
        else:
            _logger.error("%s OrderManager cancel order is not registered", self.name)

    def on_fill(self, fill_event: FillEvent):
        """
        On receive fill_event from broker.

        Parameters
        ----------
            fill_event : FillEvent
                Fill event from broker.
        """
        if fill_event.fill_id in self.fill_dict:
            _logger.error("%s fill exists", self.name)
        else:
            self.fill_dict[fill_event.fill_id] = fill_event

            if fill_event.order_id in self.order_dict:
                self.order_dict[fill_event.order_id].fill_price = (
                    fill_event.fill_price * fill_event.fill_size
                    + self.order_dict[fill_event.order_id].fill_price
                    * self.order_dict[fill_event.order_id].fill_size
                ) / (
                    self.order_dict[fill_event.order_id].fill_size
                    + fill_event.fill_size
                )
                self.order_dict[fill_event.order_id].fill_size += fill_event.fill_size

                if (
                    self.order_dict[fill_event.order_id].order_size
                    == self.order_dict[fill_event.order_id].fill_size
                ):
                    self.order_dict[
                        fill_event.order_id
                    ].order_status = OrderStatus.FILLED
                    if fill_event.order_id in self.standing_order_set:
                        self.standing_order_set.remove(fill_event.order_id)
                else:
                    self.order_dict[
                        fill_event.order_id
                    ].order_status = OrderStatus.PARTIALLY_FILLED
            else:
                _logger.error(
                    "%s Fill event %s has no matching order %s",
                    self.name,
                    fill_event.fill_id,
                    fill_event.order_id,
                )

    def retrieve_order(self, order_id: int):
        """
        Retrieve order by order_id.

        Parameters
        ----------
            order_id : int
                Order id.
        """
        try:
            return self.order_dict[order_id]
        except:  # pylint: disable=bare-except
            return None

    def retrieve_fill(self, fill_id: int):
        """
        Retrieve fill by fill_id.

        Parameters
        ----------
            fill_id : int
                Fill id.
        """
        try:
            return self.fill_dict[fill_id]
        except:  # pylint: disable=bare-except
            return None

    def retrieve_standing_orders(self):
        """
        Retrieve standing orders.
        """
        oids = []
        for oid in self.standing_order_set:
            if oid in self.order_dict:
                if (
                    self.order_dict[oid].order_status < OrderStatus.FILLED
                ):  # has standing order
                    oids.append(oid)
        return oids
