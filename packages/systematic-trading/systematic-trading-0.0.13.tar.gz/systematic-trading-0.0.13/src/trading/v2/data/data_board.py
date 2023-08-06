"""
Databoard for trading.
"""
import pandas as pd


class DataBoard:
    """
    Data tracker that holds current market data info
    """

    def __init__(self):
        self._hist_data_dict = {}
        self._current_data_dict = {}
        self._current_time = None
        self._placeholder = "PLACEHOLDER"
        self._data_index = None
        self._data_index_data_stream = None

    def initialize_hist_data(self, data_key: str, data: dict) -> None:
        """
        Initialize historical data.

        Parameters
        ----------
            data_key: str
                Key for the data

            data: dict
                Data dictionary.
        """
        self._hist_data_dict[data_key] = data

    def on_tick(self, tick) -> None:
        """
        On tick event.

        Parameters
        ----------
            tick: TickEvent
                Tick event.
        """
        if tick.full_symbol not in self._current_data_dict:
            self._current_data_dict[tick.full_symbol] = None

        self._current_data_dict[tick.full_symbol] = tick
        self._current_time = tick.timestamp

    def get_last_price(self, symbol: str) -> float:
        """
        Returns last price for a given ticker
        because self._current_time has not been updated by current tick.

        Parameters
        ----------
            symbol: str
                Ticker symbol.
        """
        return self.get_current_price(symbol, self._current_time)

    def get_current_price(self, symbol: str, timestamp: int) -> float:
        """
        Returns the most recent price for a given ticker
        based on current timestamp updated outside of data_board.

        Parameters
        ----------
            symbol: str
                Ticker symbol.

            timestamp: int
                Timestamp.
        """
        if symbol in self._current_data_dict:
            return self._current_data_dict[symbol].price
        if symbol in self._hist_data_dict:
            return self._hist_data_dict[symbol].loc[timestamp, "Close"]
        if (
            symbol[:-5] in self._hist_data_dict
        ):  # FUT root symbol e.g. CL, -5 assumes CLZ2020
            return self._hist_data_dict[symbol[:-5]].loc[
                timestamp, symbol
            ]  # column series up to timestamp inclusive
        return None

    def get_last_timestamp(self, symbol: str) -> int:
        """
        Returns the most recent timestamp for a given ticker.

        Parameters
        ----------
            symbol: str
                Ticker symbol.

        Returns
        -------
            int: Timestamp.
        """
        if symbol in self._current_data_dict:
            return self._current_data_dict[symbol].timestamp
        if self._placeholder in self._current_data_dict:
            return self._current_data_dict[self._placeholder].timestamp
        return self._current_time

    def get_current_timestamp(self):
        """
        Retrieve current timestamp.

        Returns
        -------
            int: Current timestamp.
        """
        return self._current_time

    def get_hist_price(self, symbol: str, timestamp: int) -> float:
        """
        Get historical price for a given symbol and timestamp.

        Parameters
        ----------
            symbol: str
                Ticker symbol.

            timestamp: int
                Timestamp.

        Returns
        -------
            float: Price.
        """
        if symbol in self._hist_data_dict:
            return self._hist_data_dict[symbol][:timestamp]  # up to timestamp inclusive
        if symbol[:-5] in self._hist_data_dict:  # FUT root symbol e.g. CL
            return self._hist_data_dict[symbol[:-5]][symbol][
                :timestamp
            ]  # column series up to timestamp inclusive
        return None

    def get_hist_sym_time_index(self, symbol: str) -> pd.DatetimeIndex:
        """
        Retrieve historical calendar for a symbol
        this is not look forward.

        Parameters
        ----------
            symbol: str
                Ticker symbol.
        """
        if symbol in self._hist_data_dict:
            return self._hist_data_dict[symbol].index
        if symbol[:-5] in self._hist_data_dict:  # FUT root symbol e.g. CL
            return self._hist_data_dict[symbol[:-5]].index
        return None

    def get_hist_time_index(self):
        """
        Retrieve historical calendar this is not look forwward.
        """
        if self._data_index is None:
            for value in self._hist_data_dict.values():
                if self._data_index is None:
                    self._data_index = value.index
                else:
                    # pylint: disable=attribute-defined-outside-init
                    self._data_index_data_stream = self._data_index.join(
                        value.index,
                        how="outer",
                        sort=True,
                    )

        return self._data_index
