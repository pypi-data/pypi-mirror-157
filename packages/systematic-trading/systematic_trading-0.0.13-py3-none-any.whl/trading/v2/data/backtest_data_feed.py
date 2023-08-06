"""
Backtest data feed.
"""
import pandas as pd

from .data_feed_base import DataFeedBase
from .tick_event import TickEvent


class BacktestDataFeed(DataFeedBase):
    """
    BacktestDataFeed uses PLACEHOLDER to stream_next;
    actual data comes from data_board.get_hist_price
    This is an easy way to handle multiple sources
    """

    def __init__(self, start_date=None, end_date=None) -> None:
        self._end_date = end_date
        self._start_date = start_date
        self._data_stream = None
        self._data_stream_iter = None

    def set_data_source(self, data: pd.DataFrame):
        """
        Set the data source.

        Parameters
        ----------
            data: pd.DataFrame
                The data source.
        """
        if self._data_stream is None:
            self._data_stream = data.index
        else:
            self._data_stream = self._data_stream.join(
                data.index, how="outer", sort=True
            )

    def subscribe_market_data(self, symbols=None):
        """
        Subscribe to market data.

        Parameters
        ----------
            symbols: list of str
                List of symbols to subscribe to.
        """
        if self._start_date:
            if self._end_date:
                self._data_stream = self._data_stream[
                    (self._data_stream >= self._start_date)
                    & (self._data_stream <= self._end_date)
                ]
            else:
                self._data_stream = self._data_stream[
                    self._data_stream >= self._start_date
                ]

        self._data_stream_iter = self._data_stream.iter()

    def unsubscribe_market_data(self, symbols=None):
        """
        Unsubscribe from market data.

        Parameters
        ----------
            symbols: list of str
                List of symbols to unsubscribe from.
        """

    def stream_next(self):
        """
        Place the next TickEvent into the event queue.
        """
        index = next(self._data_stream_iter)

        tick_event = TickEvent()
        tick_event.full_symbol = "PLACEHOLDER"  # place holders
        tick_event.timestamp = index

        return tick_event
