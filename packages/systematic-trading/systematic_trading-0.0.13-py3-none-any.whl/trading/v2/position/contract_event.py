"""
Contract event.
"""

from ..event.event import Event, EventType


class ContractEvent(Event):
    """
    Also serve as contract
    """

    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.event_type = EventType.CONTRACT
        self.full_symbol = ""
        self.local_name = ""
        self.mininum_tick = ""
