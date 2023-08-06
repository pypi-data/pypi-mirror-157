"""
Bar event module.
"""
import pandas as pd
from ..event.event import Event, EventType


class BarEvent(Event):
    # pylint: disable=too-many-instance-attributes
    """
    Bar event, aggregated from TickEvent
    """

    def __init__(self):
        """
        Initialises bar
        """
        self.event_type = EventType.BAR
        self.bar_start_time = pd.Timestamp("1970-01-01", tz="UTC")
        self.interval = 86400  # 1day in secs = 24hrs * 60min * 60sec
        self.full_symbol = ""
        self.open_price = 0.0
        self.high_price = 0.0
        self.low_price = 0.0
        self.close_price = 0.0
        self.adj_close_price = 0.0
        self.volume = 0

    def bar_end_time(self):
        """
        Bar end time.
        """
        # To be consistent with (daily) bar backtest, bar_end_time is set to be bar_start_time
        return self.bar_start_time
        # return self.bar_start_time + pd.Timedelta(seconds=self.interval)

    def __str__(self):
        return (
            f"Time: {self.bar_start_time}, Symbol: {self.full_symbol}, Interval: {self.interval}, "
            f"Open: {self.open_price}, High: {self.high_price}, Low: {self.low_price}, "
            f"Close: {self.close_price}, Adj Close: {self.adj_close_price}, Volume: {self.volume}"
        )
