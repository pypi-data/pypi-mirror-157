"""
Brokerage base module.
"""
from abc import abstractmethod


class BrokerageBase:
    """
    Brokerage base class.
    """

    @abstractmethod
    def place_order(self, order_event):
        """
        Place order.
        """
        raise NotImplementedError("Implement this in your derived class")

    @abstractmethod
    def cancel_order(self, order_id):
        """
        Cancel order.
        """
        raise NotImplementedError("Implement this in your derived class")

    @abstractmethod
    def next_order_id(self):
        """
        Get next order id.
        """
        raise NotImplementedError("Implement this in your derived class")

    # pylint: disable=unused-private-member
    @abstractmethod
    def __calculate_commission(self, full_symbol, fill_price, fill_size):
        """
        Calculate commision. By default it uses IB commission charges.
        """
        raise NotImplementedError("Implement this in your derived class")
