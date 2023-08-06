"""
Event module.
"""
from enum import Enum


class EventType(Enum):
    """
    Event type.
    """

    UNDEFINED = -1
    TICK = 0
    BAR = 1
    ORDER = 2
    FILL = 3
    CANCEL = 4
    ORDERSTATUS = 5
    ACCOUNT = 6
    POSITION = 7
    CONTRACT = 8
    HISTORICAL = 9
    TIMER = 10
    LOG = 11


class Event(object):
    """
    Base Event class for event-driven system
    """

    event_type = EventType.UNDEFINED

    @property
    def typename(self):
        """
        Type of event.
        """
        return self.event_type.name


class LogEvent(Event):
    """
    Log event:
    TODO seperate ErrorEvent
    """

    def __init__(self):
        self.event_type = EventType.LOG
        self.timestamp = ""
        self.content = ""
