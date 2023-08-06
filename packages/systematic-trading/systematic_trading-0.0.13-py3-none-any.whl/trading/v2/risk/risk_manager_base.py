"""
Risk manager base class.
"""
from abc import ABCMeta, abstractmethod

from ..order.order_event import OrderEvent


class RiskManagerBase(metaclass=ABCMeta):
    """
    RiskManager base class.
    """

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def order_in_compliance(
        self, order: OrderEvent, strategy_manager: "StrategyManager" = None
    ):
        """
        Order in compliance.

        Parameters
        ----------
            order : Order
                Order.

            strategy_manager : StrategyManager
                Strategy manager.
        """
        raise NotImplementedError("order_in_compliance should be implemented")
