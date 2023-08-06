"""
Transaction recorder
"""
from abc import ABCMeta, abstractmethod

from ..event.event import Event


class AbstractTradeRecorder(object):
    """
    Transaction recorder
    """

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
