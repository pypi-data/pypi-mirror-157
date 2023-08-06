"""
Contract event.
"""

from ..event.event import *


class ContractEvent(Event):
    """
    Also serve as contract
    """

    def __init__(self):
        self.event_type = EventType.CONTRACT
        self.full_symbol = ""
        self.local_name = ""
        self.mininum_tick = ""
