"""
Position manager.
"""
from datetime import datetime
import logging

from .contract_event import ContractEvent
from ..data.data_board import DataBoard
from ..order.fill_event import FillEvent
from .position_event import PositionEvent

_logger = logging.getLogger(__name__)


class PositionManager:
    """
    Position manager.
    """

    def __init__(self, name):
        """ """
        self.name = name
        self.initial_capital = 0
        self.cash = 0
        # current total value after market to market, before trades from strategy.
        # After-trades calculated in performanace manager
        self.current_total_capital = 0
        self.contracts = {}  # symbol ==> contract
        self.positions = {}  # symbol ==> positions
        self.instrument_meta = {}  # sym ==> instrument_meta

    def set_instrument_meta(self, instrument_meta_dict: dict):
        """
        Set instrument meta data.

        Parameters
        ----------
            instrument_meta_dict : dict
                Instrument meta data.
        """
        self.instrument_meta = instrument_meta_dict

    def set_capital(self, initial_capital: float):
        """
        Set initial capital.

        Parameters
        ----------
            initial_capital : float
                Initial capital.
        """
        self.initial_capital = initial_capital

    def reset(self):
        """
        Reset position manager.
        """
        self.cash = self.initial_capital
        self.current_total_capital = self.initial_capital
        self.contracts.clear()
        self.positions.clear()

    def get_holdings_count(self):
        """
        Get number of holdings.
        """
        number = 0
        for position in self.positions.values():
            if position.size != 0:
                number += 1
        return number

    def get_position_size(self, symbol: str):
        """
        Get position size.

        Parameters
        ----------
            symbol : str
                Symbol.
        """
        if symbol in self.positions:
            return self.positions[symbol].size
        return 0

    def get_cash(self):
        """
        Get cash.
        """
        return self.cash

    def get_total_pnl(self):
        """
        Get total pnl.
        """
        total_pnl = 0
        for _, pos in self.positions.items():
            realized_pnl, unrealized_pnl = pos.get_current_pnl()
            total_pnl = total_pnl + realized_pnl + unrealized_pnl
        return total_pnl

    def on_contract(self, contract: ContractEvent):
        """
        On contract event.

        Parameters
        ----------
            contract : ContractEvent
                Contract event.
        """
        if contract.full_symbol not in self.contracts:
            self.contracts[contract.full_symbol] = contract
            _logger.info(
                "%s Contract %s information received. ",
                self.name,
                contract.full_symbol,
            )
        else:
            _logger.info(
                "%s Contract %s information already exists ",
                self.name,
                contract.full_symbol,
            )

    def on_position(self, pos_event: PositionEvent):
        """
        Respond to updatePortfolio; global position_manager only.

        Parameters
        ----------
            pos_event : PositionEvent
                Position event.
        """
        pos = pos_event.to_position()
        self.positions[pos.full_symbol] = pos

    def on_fill(self, fill_event: FillEvent):
        """
        This works only on stocks.
        TODO: consider margin

        Parameters
        ----------
            fill_event : FillEvent
                Fill event.
        """
        # sell will get cash back
        if fill_event.full_symbol in self.instrument_meta.keys():
            multiplier = self.instrument_meta[fill_event.full_symbol]["Multiplier"]
        else:
            multiplier = 1

        self.cash -= (
            fill_event.fill_size * fill_event.fill_price
        ) * multiplier + fill_event.commission
        self.current_total_capital -= fill_event.commission  # commission is a cost

        if fill_event.full_symbol in self.positions:  # adjust existing position
            self.positions[fill_event.full_symbol].on_fill(
                fill_event, multiplier, self.name
            )
        else:
            self.positions[fill_event.full_symbol] = fill_event.to_position(multiplier)

    def mark_to_market(
        self,
        time_stamp: datetime,
        symbol: str,
        last_price: float,
        data_board: DataBoard,
    ):
        """
        from previous timestamp to current timestamp. Pnl from holdings
        """
        if symbol == "PLACEHOLDER":  # backtest placeholder, update all
            for sym, pos in self.positions.items():
                if sym in self.instrument_meta.keys():
                    multiplier = self.instrument_meta[sym]["Multiplier"]
                else:
                    multiplier = 1
                real_last_price = data_board.get_current_price(
                    sym, time_stamp
                )  # not PLACEHOLDER
                pos.mark_to_market(real_last_price, multiplier)
                # data board not updated yet; get_last_time return previous time_stamp
                self.current_total_capital += (
                    pos.size
                    * (real_last_price - data_board.get_last_price(sym))
                    * multiplier
                )
        elif symbol in self.positions:
            # this is a quick way based on one symbol; actual pnl should sum up across positions
            if symbol in self.instrument_meta.keys():
                multiplier = self.instrument_meta[symbol]["Multiplier"]
            else:
                multiplier = 1

            self.positions[symbol].mark_to_market(last_price, multiplier)
            prev_price = data_board.get_last_price(symbol)
            if prev_price is not None:  # in case data board hasn't been updated/empty
                self.current_total_capital += (
                    self.positions[symbol].size * (last_price - prev_price) * multiplier
                )
