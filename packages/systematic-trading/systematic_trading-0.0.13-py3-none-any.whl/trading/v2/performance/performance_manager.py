"""
Performance manager.
"""
from datetime import datetime
import logging

import numpy as np
import pandas as pd
from ..data.data_board import DataBoard
from ..order.fill_event import FillEvent
from ..position.position_manager import PositionManager


_logger = logging.getLogger(__name__)


class PerformanceManager:
    """
    https://www.quantopian.com/docs/api-reference/pyfolio-api-reference
    Record equity, positions, and trades in accordance to pyfolio format
    First date will be the first data start date
    """

    def __init__(self, instrument_meta: dict):
        """
        Parameters
        ----------
            instrument_meta: dict
                The instrument meta.
        """
        self._symbols = []
        self.instrument_meta = instrument_meta  # sym ==> meta

        self._equity = None
        self._df_positions = None
        self._df_trades = None
        self._realized_pnl = 0.0
        self._unrealized_pnl = 0.0

    @property
    def df_positions(self):
        """
        Get the positions dataframe.
        """
        return self._df_positions

    @property
    def df_trades(self):
        """
        Get the trades dataframe.
        """
        return self._df_trades

    @property
    def equity(self):
        """
        Return the equity.
        """
        return self._equity

    def add_watch(self, data_key: str, data: pd.DataFrame):
        """
        Add a watch to the performance manager.

        Parameters
        ----------
            data_key: str
                The key of the data to be watched.

            data: pd.DataFrame
                The data to be watched.
        """
        if "Close" in data.columns:  # OHLCV
            self._symbols.append(data_key)
        else:  # CLZ20, CLZ21
            self._symbols.extend(data.columns)

    #  or each sid
    def reset(self):
        """
        Reset the performance manager.
        """
        self._realized_pnl = 0.0
        self._unrealized_pnl = 0.0

        self._equity = pd.Series(dtype=np.float64)  # equity line
        self._equity.name = "total"

        self._df_positions = pd.DataFrame(
            columns=self._symbols + ["cash"], dtype=np.float64
        )
        self._df_trades = pd.DataFrame(
            np.empty(
                0,
                dtype=np.dtype(
                    [("amount", np.int64), ("price", np.float64), ("symbol", np.str)]
                ),
            )
        )
        # self._df_trades.amount = self._df_trades.amount.astype(int)     # pyfolio transactions

    def on_fill(self, fill_event: FillEvent):
        """
        On a fill, update the performance manager.

        Parameters
        ----------
            fill_event: FillEvent
                The fill event.
        """
        # self._df_trades.loc[fill_event.timestamp] = [
        #   fill_event.fill_size, fill_event.fill_price, fill_event.full_symbol]
        self._df_trades = self._df_trades.append(
            pd.DataFrame(
                {
                    "amount": [int(fill_event.fill_size)],
                    "price": [fill_event.fill_price],
                    "symbol": [fill_event.full_symbol],
                },
                index=[fill_event.fill_time],
            )
        )

    def update_performance(
        self,
        current_time: datetime,
        position_manager: PositionManager,
        data_board: DataBoard,
    ):
        """
        Update previous time/date.

        Parameters
        ----------
            current_time: datetime
                The current time.

            position_manager: PositionManager
                The position manager.

            data_board: DataBoard
                The data board.
        """
        if self._equity.empty:  # no previous day
            self._equity[current_time] = 0.0

        # on a new time/date, calculate the performances for previous time/date
        if current_time != self._equity.index[-1]:
            performance_time = self._equity.index[-1]
        else:
            # When a new data date comes in, it calcuates performances for the previous day
            # This leaves the last date not updated.
            # So we call the update explicitly
            performance_time = current_time

        equity = 0.0
        self._df_positions.loc[performance_time] = [0] * len(self._df_positions.columns)
        for sym, pos in position_manager.positions.items():
            if sym in self.instrument_meta.keys():
                multiplier = self.instrument_meta[sym]["Multiplier"]
            else:
                multiplier = 1

            # data_board (timestamp) hasn't been updated yet
            if pos.size == 0:  # skip empty size
                continue
            equity += pos.size * data_board.get_last_price(sym) * multiplier
            self._df_positions.loc[performance_time, sym] = (
                pos.size * data_board.get_last_price(sym) * multiplier
            )

        self._df_positions.loc[performance_time, "cash"] = position_manager.cash
        self._equity[performance_time] = equity + position_manager.cash
        self._df_positions.loc[performance_time, "total"] = self._equity[
            performance_time
        ]

        if performance_time != current_time:  # not final day
            self._equity[current_time] = 0.0  # add new date
        else:  # final day, re-arrange column order
            self._df_positions = self._df_positions[self._symbols + ["cash"]]
