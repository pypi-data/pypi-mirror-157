"""
Risk manager base class.
"""
from abc import ABCMeta, abstractmethod

from ..order.order_event import OrderEvent
from ..strategy.strategy_manager import StrategyManager


class RiskManagerBase(metaclass=ABCMeta):
    """
    RiskManager base class.
    """

    @abstractmethod
    def order_in_compliance(
        self, o: OrderEvent, strategy_manager: StrategyManager = None
    ):
        """
        Order in compliance.

        Parameters
        ----------
            o : Order
                Order.

            strategy_manager : StrategyManager
                Strategy manager.
        """
        raise NotImplementedError("order_in_compliance should be implemented")
