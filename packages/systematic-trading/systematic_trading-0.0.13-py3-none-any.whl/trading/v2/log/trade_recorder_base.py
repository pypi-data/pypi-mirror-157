"""
Transaction recorder
"""
from abc import ABCMeta, abstractmethod

from ..event.event import Event


class AbstractTradeRecorder:
    """
    Transaction recorder
    """

    # pylint: disable=too-few-public-methods

    __metaclass__ = ABCMeta

    @abstractmethod
    def record_trade(self, fill: Event):
        """
        Logs fill event

        Parameters
        ----------
            fill : Event
                Fill event
        """
        raise NotImplementedError("Should implement record_trade()")
