"""
Strategy manager.
"""
import logging
from datetime import datetime, timedelta
from trading.v2.order.fill_event import FillEvent

from trading.v2.position.position import Position

from ..brokerage.backtest_brokerage import BacktestBrokerage
from ..data.data_board import DataBoard
from ..data.tick_event import TickEvent
from ..order.order_event import OrderEvent
from ..order.order_manager import OrderManager
from ..order.order_status import OrderStatus
from ..position.position_manager import PositionManager
from ..risk.risk_manager import RiskManager

_logger = logging.getLogger(__name__)


class StrategyManager:
    """
    Strategy manager will check with risk manager before send out orders
    """

    # pylint: disable=too-many-instance-attributes,too-many-public-methods

    def __init__(
        self,
        config: dict,
        broker: BacktestBrokerage,
        order_manager: OrderManager,
        position_manager: PositionManager,
        risk_manager: RiskManager,
        data_board: DataBoard,
        instrument_meta: dict,
    ):
        """
        Current design: oversees all strategies/traders,
        check with risk managers before send out orders
        let strategy manager to track strategy position for each strategy,
        with the help from order manager.

        Parameters
        ----------
            config: dict
                Config file.

            broker: BacktestBrokerage
                Brokerage instance.

            order_manager: OrderManager
                Order manager instance.

            position_manager: PositionManager
                Position manager instance.

            risk_manager: RiskManager
                Risk manager instance.

            data_board: DataBoard
                Data board instance.
        """
        # pylint: disable=too-many-arguments
        self._config = config
        self._broker = broker
        self._order_manager = order_manager
        self._position_manager = position_manager
        self._risk_manager = risk_manager
        self._data_board = data_board
        self._strategy_dict = {}  # sid ==> strategy
        self._instrument_meta = instrument_meta  # symbol ==> instrument_meta
        self._tick_strategy_dict = {}  # sym -> list of strategy
        self._sid_oid_dict = {
            0: [],
            -1: [],
        }  # sid ==> oid list; 0: manual; -1: unknown source

    def load_strategy(self, strat_dict: dict):
        """
        Load strategy from dict.

        Parameters
        ----------
            strat_dict: dict
                Strategy dict.
        """
        # pylint: disable=too-many-branches
        sid = 1  # 0 is manual discretionary trade, or not found
        # similar to backtest; strategy sets capital, params, and symbols
        for key, value in strat_dict.items():
            value.id = sid
            sid += 1
            value.name = key
            if value.name in self._config["strategy"]:
                value.active = self._config["strategy"][value.name]["active"]
                value.set_capital(
                    self._config["strategy"][value.name]["capital"]
                )  # float
                value.set_params(self._config["strategy"][value.name]["params"])  # dict
                value.set_symbols(
                    self._config["strategy"][value.name]["symbols"]
                )  # list

                # yaml converts to seconds
                if "order_start_time" in self._config["strategy"][value.name].keys():
                    if isinstance(
                        self._config["strategy"][value.name]["order_start_time"], int
                    ):
                        self._config["strategy"][value.name]["order_start_time"] = str(
                            timedelta(
                                seconds=self._config["strategy"][value.name][
                                    "order_start_time"
                                ]
                            )
                        )
                if "order_end_time" in self._config["strategy"][value.name].keys():
                    if isinstance(
                        self._config["strategy"][value.name]["order_end_time"], int
                    ):
                        self._config["strategy"][value.name]["order_end_time"] = str(
                            timedelta(
                                seconds=self._config["strategy"][value.name][
                                    "order_end_time"
                                ]
                            )
                        )

            self._strategy_dict[value.id] = value
            self._sid_oid_dict[value.id] = []  # record its orders
            for sym in value.symbols:
                if sym not in self._instrument_meta.keys():
                    # find first digit position
                    sym_split = sym.split(" ")
                    index = 0
                    for index, character in enumerate(sym_split[0]):
                        if character.isdigit():
                            break
                    if index < len(sym_split[0]):
                        sym_root = sym_split[0][: index - 1]
                        if sym_root in self._instrument_meta.keys():
                            self._instrument_meta[sym] = self._instrument_meta[
                                sym_root
                            ]  # add for quick access

                if sym in self._tick_strategy_dict:
                    self._tick_strategy_dict[sym].append(value.id)
                else:
                    self._tick_strategy_dict[sym] = [value.id]
                if sym in self._broker.market_data_subscription_reverse_dict:
                    continue
                _logger.info("add %s", sym)
                self._broker.market_data_subscription_reverse_dict[sym] = -1

            value.on_init(self, self._data_board, self._instrument_meta)

    @property
    def config(self):
        """
        Config file.
        """
        return self._config

    @property
    def order_manager(self):
        """
        Order manager instance.
        """
        return self._order_manager

    @property
    def position_manager(self):
        """
        Position manager instance.
        """
        return self._position_manager

    @property
    def strategy_dict(self):
        """
        Strategy dict.
        """
        return self._strategy_dict

    def start_strategy(self, sid: int):
        """
        Start strategy.

        Parameters
        ----------
            sid: int
                Strategy id.
        """
        self._strategy_dict[sid].active = True

    def stop_strategy(self, sid: int):
        """
        Stop strategy.

        Parameters
        ----------
            sid: int
                Strategy id.
        """
        self._strategy_dict[sid].active = False

    def pause_strategy(self, sid: int):
        """
        Pause strategy.

        Parameters
        ----------
            sid: int
                Strategy id.
        """
        self._strategy_dict[sid].active = False

    def start_all(self):
        """
        Start all strategies.
        """
        for value in self._strategy_dict.values():
            value.active = True

    def stop_all(self):
        """
        Stop all strategies.
        """
        for value in self._strategy_dict.values():
            value.active = False

    def place_order(self, order: OrderEvent, check_risk: bool = True):
        """
        Currently it puts order directly with broker; e.g. by simplying calling ib.placeOrder method
        Because order is placed directly; all subsequent on_order messages are order status updates
        TODO, use an outbound queue to send orders
        1. check with risk manager

        Parameters
        ----------
            order: OrderEvent
                Order event.

            check_risk: bool (default: True)
                Check risk.
        """

        order_check = True
        if check_risk:
            order_check = self._risk_manager.order_in_compliance(order, self)

        # 2. if green light
        if not order_check:
            return

        # 2.a record
        oid = self._broker.orderid
        self._broker.orderid += 1
        order.order_id = oid
        order.order_status = OrderStatus.NEWBORN
        self._sid_oid_dict[order.source].append(oid)
        # feedback newborn status
        self._order_manager.on_order_status(order)
        if order.source in self._strategy_dict:  # in case it is not placed by strategy
            self._strategy_dict[order.source].on_order_status(order)

        # 2.b place order
        self._broker.place_order(order)

    def cancel_order(self, oid: int):
        """
        Cancel order.

        Parameters
        ----------
            oid: int
                Order id.
        """
        self._order_manager.on_cancel(oid)
        # self._strategy_dict[sid].on_cancel(oid)  # This is moved to strategy_base
        self._broker.cancel_order(oid)

    def cancel_strategy(self, sid: int):
        """
        Call strategy cancel to take care of strategy order_manager.

        Parameters
        ----------
            sid: int
                Strategy id.
        """
        if sid not in self._strategy_dict:
            _logger.error("Cancel strategy can not locate strategy id %s", sid)
        else:
            self._strategy_dict[sid].cancel_all()

    def cancel_all(self):
        """
        Cancel all orders.
        """
        for strategy in self._strategy_dict.values():
            strategy.cancel_all()

    def flat_strategy(self, sid: int):
        """
        Flat with MARKET order (default)
        Assume each strategy track its own positions
        TODO: should turn off strategy?

        Parameters
        ----------
            sid: int
                Strategy id.
        """
        if sid not in self._strategy_dict:
            _logger.error("Flat strategy can not locate strategy id %s", sid)

        for sym, pos in self._strategy_dict[sid].position_manager.positions.items():
            if pos.size != 0:
                order = OrderEvent()
                order.full_symbol = sym
                order.order_size = -pos.size
                order.source = 0  # mannual flat
                order.create_time = datetime.now().strftime("%H:%M:%S.%f")
                self.place_order(
                    order, check_risk=False
                )  # flat strategy doesnot cehck risk

    def flat_all(self):
        """
        Flat all according to position_manager
        TODO: should turn off all strategies?
        """
        for sym, pos in self._position_manager.positions.items():
            if pos.size != 0:
                order = OrderEvent()
                order.full_symbol = sym
                order.order_size = -pos.size
                order.source = 0
                order.create_time = datetime.now().strftime("%H:%M:%S.%f")
                self.place_order(
                    order, check_risk=False
                )  # flat strategy doesnot cehck risk

    def on_tick(self, k: TickEvent):
        """
        On tick.

        Parameters
        ----------
            k: TickEvent
                Tick event.
        """
        if k.full_symbol in self._tick_strategy_dict:
            s_list = self._tick_strategy_dict[k.full_symbol]
            for sid in s_list:
                if self._strategy_dict[sid].active:
                    self._strategy_dict[sid].on_tick(k)

    def on_position(self, pos: Position):
        """
        Get initial position.
        Read from config file instead.

        Parameters
        ----------
            pos: Position
                Position.
        """

    def on_order_status(self, order_event: OrderEvent):
        """
        On order status.
        TODO: check if source is working

        Parameters
        ----------
            order_event: OrderEvent
                Order event.
        """
        sid = order_event.source
        if sid in self._strategy_dict:
            self._strategy_dict[sid].on_order_status(order_event)
        else:
            _logger.info(
                "strategy manager doesnt hold the oid %s to set status %s, "
                "possibly from outside of the system",
                order_event.order_id,
                order_event.order_status,
            )

    def on_cancel(self, order_event: OrderEvent):
        """
        On cancel.
        TODO no need for this

        Parameters
        ----------
            order_event: OrderEvent
                Order event.
        """
        sid = order_event.source
        if sid in self._strategy_dict:
            self._strategy_dict[sid].on_order_status(order_event)
        else:
            _logger.info(
                "strategy manager doesnt hold the oid %s to cancel, "
                "possibly from outside of the system",
                order_event.order_id,
            )

    def on_fill(self, fill_event: FillEvent):
        """
        Assign fill ordering to order id ==> strategy id
        TODO: check fill_event source; if not, fix it or use fill_event.order_id

        Parameters
        ----------
            fill_event: FillEvent
                Fill event.
        """
        sid = fill_event.source
        if sid in self._strategy_dict:
            self._strategy_dict[sid].on_fill(fill_event)
        else:
            _logger.info(
                "strategy manager doesnt hold the oid %s to fill, "
                "possibly from outside of the system",
                fill_event.order_id,
            )
