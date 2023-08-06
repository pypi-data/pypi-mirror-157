"""
Risk manager.
"""
import logging

from ..order.order_event import OrderEvent
from .risk_manager_base import RiskManagerBase

_logger = logging.getLogger(__name__)


class PassThroughRiskManager(RiskManagerBase):
    """
    Pass through risk manager.
    """

    # pylint: disable=too-few-public-methods

    def order_in_compliance(
        self, order: OrderEvent, strategy_manager: "StrategyManager" = None
    ):
        """
        Pass through the order without constraints.

        Parameters
        ----------
            order : Order
                Order.

            strategy_manager : StrategyManager
                Strategy manager.
        """
        return True


class RiskManager(RiskManagerBase):
    """
    Risk manager.
    """

    # pylint: disable=too-few-public-methods

    def order_in_compliance(
        self, order: OrderEvent, strategy_manager: "StrategyManager" = None
    ):
        """
        Check if the order is in compliance with the risk manager.

        Parameters
        ----------
            order : Order
                Order.

            strategy_manager : StrategyManager
                Strategy manager.
        """
        # pylint: disable=too-many-branches,too-many-return-statements,too-many-statements
        # 1. check time str hh:mm:ss
        if (
            "order_start_time"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["order_start_time"]
                is not None
            ):
                if (
                    order.create_time
                    < strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["order_start_time"]
                ):
                    _logger.error(
                        "Order start time breach %s: %s / %s",
                        order.source,
                        order.create_time,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["order_start_time"],
                    )
                    return False
        if (
            "order_end_time"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                not strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["order_end_time"]
                is None
            ):
                if (
                    order.create_time
                    > strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["order_end_time"]
                ):
                    _logger.error(
                        "Order end time breach %s: %s / %s",
                        order.source,
                        order.create_time,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["order_end_time"],
                    )
                    return False

        # 2. single trade limit; integer
        if (
            "single_trade_limit"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                not strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["single_trade_limit"]
                is None
            ):
                if (
                    abs(order.order_size)
                    > strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["single_trade_limit"]
                ):
                    _logger.error(
                        "Order single trade limit breach %s: %s / %s",
                        order.source,
                        order.order_size,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["single_trade_limit"],
                    )
                    return False

        # total # of trades
        if (
            "total_trade_limit"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                not strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["total_trade_limit"]
                is None
            ):
                number_of_trades = len(
                    strategy_manager.strategy_dict[
                        order.source
                    ].order_manager.order_dict
                ) - len(
                    strategy_manager.strategy_dict[
                        order.source
                    ].order_manager.canceled_order_set
                )
                if (
                    number_of_trades
                    > strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["total_trade_limit"]
                ):
                    _logger.error(
                        "Order total trade limit breach %s: %s / %s",
                        order.source,
                        order.source,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["total_trade_limit"],
                    )
                    return False
        if "total_trade_limit" in strategy_manager.config.keys():
            if not strategy_manager.config["total_trade_limit"] is None:
                number_of_trades = len(strategy_manager.order_manager.order_dict) - len(
                    strategy_manager.order_manager.canceled_order_set
                )
                if number_of_trades > strategy_manager.config["total_trade_limit"]:
                    _logger.error(
                        "Order global total trade limit breach %s: %s / %s",
                        order.source,
                        number_of_trades,
                        strategy_manager.config["total_trade_limit"],
                    )
                    return False

        # cancel # limit
        if (
            "total_cancel_limit"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                not strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["total_cancel_limit"]
                is None
            ):
                number_of_cancels = len(
                    strategy_manager.strategy_dict[
                        order.source
                    ].order_manager.canceled_order_set
                )
                if (
                    number_of_cancels
                    > strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["total_cancel_limit"]
                ):
                    _logger.error(
                        "Order total cancel limit breach %s: %s / %s",
                        order.source,
                        number_of_cancels,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["total_cancel_limit"],
                    )
                    return False
        if "total_cancel_limit" in strategy_manager.config.keys():
            if not strategy_manager.config["total_cancel_limit"] is None:
                number_of_cancels = len(
                    strategy_manager.order_manager.canceled_order_set
                )
                if number_of_cancels > strategy_manager.config["total_cancel_limit"]:
                    _logger.error(
                        "Order global total cancel limit breach %s: %s / %s",
                        order.source,
                        number_of_cancels,
                        strategy_manager.config["total_cancel_limit"],
                    )
                    return False

        # active order # limit
        if (
            "total_active_limit"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                not strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["total_active_limit"]
                is None
            ):
                number_of_active_orders = len(
                    strategy_manager.strategy_dict[
                        order.source
                    ].order_manager.standing_order_set
                )
                if (
                    number_of_active_orders
                    > strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["total_active_limit"]
                ):
                    _logger.error(
                        "Order total active limit breach %s: %s / %s",
                        order.source,
                        number_of_active_orders,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["total_active_limit"],
                    )
                    return False
        if "total_active_limit" in strategy_manager.config.keys():
            if not strategy_manager.config["total_active_limit"] is None:
                number_of_active_orders = len(
                    strategy_manager.order_manager.standing_order_set
                )
                if (
                    number_of_active_orders
                    > strategy_manager.config["total_active_limit"]
                ):
                    _logger.error(
                        "Order global total active limit breach %s: %s / %s",
                        order.source,
                        number_of_active_orders,
                        strategy_manager.config["total_active_limit"],
                    )
                    return False

        # pnl; note that total loss includes open pnl from existing positions
        # (e.g. bought yesterday, carried overnight)
        if (
            "total_loss_limit"
            in strategy_manager.config["strategy"][
                strategy_manager.strategy_dict[order.source].name
            ].keys()
        ):
            if (
                not strategy_manager.config["strategy"][
                    strategy_manager.strategy_dict[order.source].name
                ]["total_loss_limit"]
                is None
            ):
                total_pnl = strategy_manager.strategy_dict[
                    order.source
                ].position_manager.get_total_pnl() * (-1.0)
                if (
                    total_pnl
                    > strategy_manager.config["strategy"][
                        strategy_manager.strategy_dict[order.source].name
                    ]["total_loss_limit"]
                ):
                    _logger.error(
                        "Order total pnl limit breach %s: %s / %s",
                        order.source,
                        total_pnl,
                        strategy_manager.config["strategy"][
                            strategy_manager.strategy_dict[order.source].name
                        ]["total_loss_limit"],
                    )
                    return False
        if "total_loss_limit" in strategy_manager.config.keys():
            if not strategy_manager.config["total_loss_limit"] is None:
                total_pnl = strategy_manager.position_manager.get_total_pnl() * (-1.0)
                if total_pnl > strategy_manager.config["total_loss_limit"]:
                    _logger.error(
                        "Order global total pnl limit breach %s: %s / %s",
                        order.source,
                        total_pnl,
                        strategy_manager.config["total_loss_limit"],
                    )
                    return False

        # TODO "check position", or risk reach; pylint: disable=fixme
        # maybe not here but periodic check
        return True
