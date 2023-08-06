"""
Strategy base module.
"""
from abc import ABCMeta
from datetime import datetime
import logging

from trading.v2.data.data_board import DataBoard

from trading.v2.strategy.strategy_manager import StrategyManager

from ..data.tick_event import TickEvent
from ..order.fill_event import FillEvent
from ..order.order_event import OrderEvent
from ..order.order_type import OrderType
from ..order import OrderManager
from ..position import PositionManager

_logger = logging.getLogger(__name__)


class StrategyBase(metaclass=ABCMeta):
    """
    Base strategy class
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """
        Initialize strategy.
        """
        self._id = -1  # id
        self.name = ""  # name
        self.symbols = []  # symbols interested
        self.strategy_manager = None  # to place order through strategy_manager
        self._data_board = None  # to get current data
        self._position_manager = PositionManager(
            self.name
        )  # track local positions and cash
        self._order_manager = OrderManager(
            self.name
        )  # manage local (standing) orders and fills

        self.active = False
        self.initialized = False

    @property
    def order_manager(self):
        """
        Order manager.
        """
        return self._order_manager

    @property
    def position_manager(self):
        """
        Position manager.
        """
        return self._position_manager

    def set_capital(self, capital: float):
        """
        Set capital.

        Parameters
        ----------
            capital : float
                Capital.
        """
        self._position_manager.set_capital(capital)

    def set_symbols(self, symbols: list):
        """
        Set symbols.

        Parameters
        ----------
            symbols : list
                Symbols.
        """
        self.symbols = symbols

    def set_name(self, name: str):
        """
        Set name.

        Parameters
        ----------
            name : str
                Name.
        """
        self.name = name
        self._position_manager.name = name
        self._order_manager.name = name

    def set_params(self, params_dict: dict = None):
        """
        Set parameters.

        Parameters
        ----------
            params_dict : dict
                Parameters.
        """
        if params_dict is not None:
            for key, value in params_dict.items():
                try:
                    setattr(self, key, value)
                except:  # pylint: disable=bare-except
                    pass

    def on_init(
        self,
        strategy_manager: StrategyManager,
        data_board: DataBoard,
        instrument_meta: dict,
    ):
        """
        On init.

        Parameters
        ----------
            strategy_manager : StrategyManager
                Strategy manager.

            data_board : DataBoard
                Data board.

            instrument_meta : dict
                Instrument meta.
        """
        self.strategy_manager = strategy_manager
        self._data_board = data_board
        self._position_manager.set_instrument_meta(instrument_meta)
        self._position_manager.reset()
        self.initialized = True

    def on_start(self):
        """
        On start.
        """
        self.active = True

    def on_stop(self):
        """
        On stop.
        """
        self.active = False

    def on_tick(self, tick_event: TickEvent):
        """
        Respond to tick.

        Parameters
        ----------
            tick_event : TickEvent
                Tick event.
        """
        # for live trading, turn off p&l tick by not calling super.on_tick()
        # for backtest, call super().on_tick() if need to track positions or npv or cash
        self._position_manager.mark_to_market(  # pylint: disable=duplicate-code
            tick_event.timestamp,
            tick_event.full_symbol,
            tick_event.price,
            self._data_board,
        )

    def on_order_status(self, order_event: OrderEvent):
        """
        On order acknowledged.

        Parameters
        ----------
            order_event : OrderEvent
                Order event.
        """
        # raise NotImplementedError("Should implement on_order_status()")
        self._order_manager.on_order_status(order_event)

    def on_fill(self, fill_event: FillEvent):
        """
        On order filled derived class call super().on_fill first.

        Parameters
        ----------
            fill_event : FillEvent
                Fill event.
        """
        self._position_manager.on_fill(fill_event)
        self._order_manager.on_fill(fill_event)

    def place_order(self, order: OrderEvent):
        """
        expect user to set up order type, order size and order price
        """
        order.source = self._id  # identify source
        if order.create_time is None:
            order.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if self.active:
            self.strategy_manager.place_order(order)

    def adjust_position(
        self, sym: str, size_from: int, size_to: int, timestamp: datetime = None
    ):
        """
        Use market order to adjust position.

        Parameters
        ----------
            sym : str
                Symbol.

            size_from : int
                Size from.

            size_to : int
                Size to.

            timestamp : datetime
                Timestamp.
        """
        if size_from == size_to:
            return
        order = OrderEvent()
        order.full_symbol = sym
        order.order_type = OrderType.MARKET
        order.order_size = size_to - size_from
        if timestamp is not None:
            order.create_time = timestamp

        self.place_order(order)

    def cancel_order(self, oid: int):
        """
        Cancel order.

        Parameters
        ----------
            oid : int
                Order id.
        """
        if oid in self._order_manager.standing_order_set:
            self._order_manager.on_cancel(oid)
            self.strategy_manager.cancel_order(oid)
        else:
            _logger.error("Not a standing order to be cancelled, sid {id}, oid %s", oid)

    def cancel_all(self):
        """
        Cancel all standing orders from this strategy id.
        """
        for oid in self._order_manager.standing_order_set:
            self._order_manager.on_cancel(oid)
            self.strategy_manager.cancel_order(oid)
