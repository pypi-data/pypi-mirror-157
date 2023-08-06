"""
Margin module.
"""
from datetime import date
import numpy as np

from .contract import Contract
from .forex import Forex
from .market_data import MarketData
from ..data.constants import get_futures


class Margin:
    """
    Margin.
    """

    def __init__(self):
        self.cache = {}
        self.forex = Forex()
        self.market_data = MarketData()

    def __adjustment_factor(self, ticker: str, day: date):
        # update of adjustment factor is done yearly
        key = f"{ticker} {day.year}"
        if key in self.cache:
            return self.cache[key]
        contract, _ = Contract(ticker=ticker, day=day).front_contract
        if not self.market_data.is_trading_day(contract=contract, day=day):
            return np.NaN
        row = self.market_data.bardata(contract=contract, day=day)
        ref_date = self.__get_ref_date(ticker=ticker)
        ref_contract, _ = Contract(ticker=ticker, day=ref_date).front_contract
        row_ref = self.market_data.bardata(contract=ref_contract, day=ref_date)
        self.cache[key] = row["Close"][0] / row_ref["Close"][0]
        return self.cache[key]

    @staticmethod
    def __get_ref_date(ticker: str):
        if ticker in ["HTE", "MBT"]:
            return date(2021, 8, 18)
        default_ref_date = date(2020, 1, 6)
        return default_ref_date

    def overnight_initial_future(self, ticker: str, day: date):
        """
        Get the initial overnight margin limit.

        Parameters
        ----------
            ticker: str
                Ticker of the instrument.

            day: date
                Date to get the initial overnight margin limit.

        Returns
        -------
            float
                Initial overnight margin limit.
        """

        currency = get_futures()[ticker]["Currency"]
        return (
            get_futures()[ticker]["OvernightInitial"]
            * self.__adjustment_factor(ticker=ticker, day=day)
            * self.forex.to_usd(currency, day)
        )

    def overnight_maintenance_future(self, ticker: str, day: date):
        """
        Get the maintenance overnight margin limit.

        Parameters
        ----------
            ticker: str
                Ticker of the instrument.

            day: date
                Date to get the maintenance overnight margin limit.

        Returns
        -------
            float
                Maintenance overnight margin limit.
        """
        currency = get_futures()[ticker]["Currency"]
        return (
            get_futures()[ticker]["OvernightMaintenance"]
            * self.__adjustment_factor(ticker=ticker, day=day)
            * self.forex.to_usd(currency, day)
        )
