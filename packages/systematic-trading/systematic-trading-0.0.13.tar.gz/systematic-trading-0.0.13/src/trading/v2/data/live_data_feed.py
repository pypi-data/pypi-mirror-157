"""
Live feed module.
"""
from datetime import datetime, timedelta
import logging


import pandas as pd
import quandl

from .data_feed_base import DataFeedBase
from ..data.bar_event import BarEvent


_logger = logging.getLogger(__name__)


# pylint: disable=abstract-method
class LiveDataFeed(DataFeedBase):
    """
    Live DataFeed class
    """

    # pylint: disable=too-many-instance-attributes,too-many-arguments

    def __init__(
        self,
        events_queue,
        init_tickers=None,
        start_date=None,
        end_date=None,
        calc_adj_returns=False,
    ):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols then creates an (optional)
        list of ticker subscriptions and associated prices.

        Parameters:
        -----------
            events_queue : Queue
                The Queue object from the backtester.

            init_tickers : list, optional
                The list of ticker symbols to initialize the
                price handler with.

            start_date : datetime, optional
                The start date of the backtest.

            end_date : datetime, optional
                The end date of the backtest.

            calc_adj_returns : bool, optional
                Calculate and store the adjusted closing price
        """
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        self.start_date = start_date
        self.end_date = end_date

        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)

        self.bar_stream = self.__merge_sort_ticker_data()
        self.calc_adj_returns = calc_adj_returns
        if self.calc_adj_returns:
            self.adj_close_returns = []

    def __open_ticker_price_online(self, ticker: str) -> None:
        """
        Opens the CSV online from yahoo finance, then store in a dictionary.

        Parameters:
        -----------
            ticker : str
                The ticker symbol to open the CSV online from yahoo finance.
        """
        if self.end_date is not None:
            end_date = self.end_date
        else:
            end_date = datetime.today()
        if self.start_date is not None:
            start_date = self.start_date
        else:
            start_date = end_date - timedelta(days=365)

        data = quandl.get(
            "wiki/" + ticker,
            start_date=start_date,
            end_date=end_date,
            authtoken="your_token",
        )
        self.tickers_data[ticker] = data
        self.tickers_data[ticker]["Ticker"] = ticker

    def __merge_sort_ticker_data(self) -> None:
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        dfm = pd.concat(self.tickers_data.values()).sort_index()
        start = None
        end = None
        if self.start_date is not None:
            start = dfm.index.searchsorted(self.start_date)
        if self.end_date is not None:
            end = dfm.index.searchsorted(self.end_date)
        # Determine how to slice
        if start is None and end is None:
            return dfm.iterrows()
        if start is not None and end is None:
            return dfm.ix[start:].iterrows()
        if start is None and end is not None:
            return dfm.ix[:end].iterrows()
        return dfm.ix[start:end].iterrows()

    def subscribe_ticker(self, ticker: str) -> None:
        """
        Subscribes the price handler to a new ticker symbol.

        Parameters
        ----------
            ticker : str
                The ticker symbol to subscribe to.
        """
        if ticker not in self.tickers:
            try:
                self.__open_ticker_price_online(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]

                close = row0["Close"]
                adj_close = row0["Adj. Close"]

                ticker_prices = {
                    "close": close,
                    "adj_close": adj_close,
                    "timestamp": dft.index[0],
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                _logger.error(
                    "Could not subscribe ticker %s as no data CSV found for pricing.",
                    ticker,
                )
        else:
            _logger.error(
                "Could not subscribe ticker %s as is already subscribed.", ticker
            )

    @staticmethod
    def __create_event(index, period, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe
        and return a BarEvent
        """
        open_price = row["Open"]
        high_price = row["High"]
        low_price = row["Low"]
        close_price = row["Close"]
        adj_close_price = row["Adj. Close"]
        volume = int(row["Volume"])
        bev = BarEvent()
        bev.bar_start_time = index
        bev.full_symbol = ticker
        bev.interval = period
        bev.open_price = open_price
        bev.high_price = high_price
        bev.low_price = low_price
        bev.close_price = close_price
        bev.volume = volume
        bev.adj_close_price = adj_close_price
        return bev

    def __store_event(self, event):
        """
        Store price event for closing price and adjusted closing price
        """
        ticker = event.ticker
        # If the calc_adj_returns flag is True, then calculate
        # and store the full list of adjusted closing price
        # percentage returns in a list
        # TODO: Make this faster pylint: disable=fixme
        if self.calc_adj_returns:
            prev_adj_close = self.tickers[ticker]["adj_close"]
            cur_adj_close = event.adj_close_price
            self.tickers[ticker]["adj_close_ret"] = cur_adj_close / prev_adj_close - 1.0
            self.adj_close_returns.append(self.tickers[ticker]["adj_close_ret"])
        self.tickers[ticker]["close"] = event.close_price
        self.tickers[ticker]["adj_close"] = event.adj_close_price
        self.tickers[ticker]["timestamp"] = event.time

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            index, row = next(self.bar_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        # Obtain all elements of the bar from the dataframe
        ticker = row["Ticker"]
        period = 86400  # Seconds in a day
        # Create the tick event for the queue
        bev = self.__create_event(index, period, ticker, row)
        # Store event
        self.__store_event(bev)
        # Send event to queue
        self.events_queue.put(bev)
