"""
Backtest engine.
"""
from datetime import datetime
import logging

import pandas as pd

from .event import EventType
from .event.backtest_event_engine import BacktestEventEngine
from .data.backtest_data_feed import BacktestDataFeed
from .data.data_board import DataBoard
from .data.tick_event import TickEvent
from .brokerage.backtest_brokerage import BacktestBrokerage
from .position.position_manager import PositionManager
from .order.fill_event import FillEvent
from .order.order_event import OrderEvent
from .order.order_manager import OrderManager
from .performance.performance_manager import PerformanceManager
from .risk.risk_manager import PassThroughRiskManager
from .strategy import StrategyBase, StrategyManager

_logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Event driven backtest engine
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        """
        Initialize backtest engine

        Parameters
        ----------
            start_date: datetime
                Start date of backtest

            end_date: datetime
                End date of backtest
        """
        self._current_time = None
        self._start_date = start_date
        self._end_date = end_date
        self.config = {}
        self.config[
            "strategy"
        ] = {}  # to be consistent with live; in backtest, strategy is set outside
        self.instrument_meta = {}  # one copy of meta dict shared across program
        self._data_feed = BacktestDataFeed(self._start_date, self._end_date)
        self._data_board = DataBoard()
        self._performance_manager = PerformanceManager(
            self.instrument_meta
        )  # send dict pointer
        self._position_manager = PositionManager("Global")
        self._position_manager.set_instrument_meta(self.instrument_meta)
        self._order_manager = OrderManager("Global")
        self._events_engine = BacktestEventEngine(self._data_feed)
        self._backtest_brokerage = BacktestBrokerage(
            self._events_engine, self._data_board
        )
        self._risk_manager = PassThroughRiskManager()
        self._strategy_manager = StrategyManager(
            self.config,
            self._backtest_brokerage,
            self._order_manager,
            self._position_manager,
            self._risk_manager,
            self._data_board,
            self.instrument_meta,
        )
        self._strategy = None

    @property
    def order_manager(self):
        """
        Order manager.
        """
        return self._order_manager

    def set_instrument_meta(self, instrument_meta: dict):
        """
        Set instrument meta.

        Parameters
        ----------
            instrument_meta: dict
                Instrument meta.
        """
        self.instrument_meta.update(instrument_meta)

    def set_capital(self, capital: float):
        """
        Set capital to the global position manager.

        Parameters
        ----------
            capital: float
                Capital.
        """
        self._position_manager.set_capital(capital)

    def set_strategy(self, strategy: StrategyBase):
        """
        Set strategy.

        Parameters
        ----------
            strategy: StrategyBase
                Strategy.
        """
        self._strategy = strategy

    def add_data(self, data_key: str, data_source: pd.DataFrame, watch: bool = True):
        """
        Add data for backtest

        Parameters
        ----------
            data_key: str
                Data key. AAPL or CL.

            data_source: pd.DataFrame
                Data source.

            watch: bool
                Whether to track position or not.
        """
        if data_key not in self.instrument_meta:
            keys = data_key.split(" ")
            # find first digit position
            for index, character in enumerate(keys[0]):
                if character.isdigit():
                    break
                if index < len(keys[0]):
                    sym_root = keys[0][: index - 1]
                    if sym_root in self.instrument_meta:
                        self.instrument_meta[data_key] = self.instrument_meta[sym_root]

        self._data_feed.set_data_source(data_source)  # get iter(datetimeindex)
        self._data_board.initialize_hist_data(data_key, data_source)
        if watch:
            self._performance_manager.add_watch(data_key, data_source)

    def _setup(self):
        """
        This needs to be run after strategy and data are loaded
        because it subscribes to market data.
        """
        ## 1. data_feed
        self._data_feed.subscribe_market_data()

        ## 4. set strategy
        self._strategy.active = True
        self._strategy_manager.load_strategy({self._strategy.name: self._strategy})

        ## 5. global performance manager and portfolio manager
        self._performance_manager.reset()
        self._position_manager.reset()

        ## 5. trade recorder
        # self._trade_recorder = ExampleTradeRecorder(output_dir)

        ## 6. wire up event handlers
        self._events_engine.register_handler(EventType.TICK, self._tick_event_handler)
        # to be consistent with current live, order is placed directly;
        # this accepts other status like status, fill, cancel
        self._events_engine.register_handler(EventType.ORDER, self._order_event_handler)
        self._events_engine.register_handler(EventType.FILL, self._fill_event_handler)

    def _tick_event_handler(self, tick_event: TickEvent):
        """
        Tick event handler.

        Parameters
        ----------
            tick_event: TickEvent
                Tick event.
        """
        self._current_time = tick_event.timestamp

        # performance update goes before position and databoard updates
        # because it updates previous day performance
        # it can't update today because orders haven't been filled yet.
        self._performance_manager.update_performance(
            self._current_time, self._position_manager, self._data_board
        )
        self._position_manager.mark_to_market(  # pylint: disable=duplicate-code
            tick_event.timestamp,
            tick_event.full_symbol,
            tick_event.price,
            self._data_board,
        )
        self._strategy.on_tick(
            tick_event
        )  # plus strategy.position_manager market to market
        # data_baord update after strategy, so it still holds price of last tick; for position MtM
        # strategy uses tick.price for current price; and use data_board.last_price
        # for previous price for backtest, this is PLACEHOLDER based on timestamp.
        # strategy pull directly from data_board hist_data for current_price;
        # and data_board.last_price for previous price
        self._data_board.on_tick(tick_event)
        # check standing orders, after databoard is updated
        self._backtest_brokerage.on_tick(tick_event)

    def _order_event_handler(self, order_event: OrderEvent):
        """
        Acknowledge order.

        Parameters
        ----------
            order_event: OrderEvent
                Order event.
        """
        # self._backtest_brokerage.place_order(order_event)
        self._order_manager.on_order_status(order_event)
        self._strategy.on_order_status(order_event)

    def _fill_event_handler(self, fill_event: FillEvent):
        """
        Fill event handler.

        Parameters
        ----------
            fill_event: FillEvent
                Fill event.
        """
        self._order_manager.on_fill(fill_event)
        self._position_manager.on_fill(fill_event)
        self._performance_manager.on_fill(fill_event)
        self._strategy.on_fill(fill_event)

    def run(self):
        """
        Run backtest
        """
        self._setup()

        self._events_engine.run()
        # explicitly update last day/time
        self._performance_manager.update_performance(
            self._current_time, self._position_manager, self._data_board
        )

        return (
            self._performance_manager.equity,
            self._performance_manager.df_positions,
            self._performance_manager.df_trades,
        )
