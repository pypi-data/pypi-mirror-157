"""
Order flag.
"""
from enum import Enum


class OrderFlag(Enum):
    """
    Order flag.
    """

    OPEN = 0  # in use
    CLOSE = 1
    CLOSE_TODAY = 2  # in use
    CLOSE_YESTERDAY = 3  # in use
