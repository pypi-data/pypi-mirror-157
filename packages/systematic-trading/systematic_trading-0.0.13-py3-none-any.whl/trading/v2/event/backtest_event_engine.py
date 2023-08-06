"""
Backtest event engine.
"""
# pylint: disable=duplicate-code
from collections import defaultdict
import logging
from queue import Empty, Queue

from .event import Event


_logger = logging.getLogger(__name__)


class BacktestEventEngine:
    """
    Event queue + a while loop to dispatch events
    """

    def __init__(self, datafeed):
        """
        Initialize handler function list
        """
        # if the data feed is active
        self._active = True

        # event queue
        self._queue = Queue()

        # pull from backtest data feed
        self._datafeed = datafeed

        # event handlers list, dict: specific event key --> handler value
        self._handlers = defaultdict(list)

    def run(self, n_steps: int = -1):
        """
        Run backtest,
        if n_steps = -1, run to the end; else run n_steps

        Parameters
        ----------
            n_steps : int
                Number of steps to run
        """
        _logger.info("Running Backtest...")
        nstep = 0
        while self._active:
            try:
                event = self._queue.get(False)
            except Empty:  # throw good exception
                if (n_steps == -1) or (nstep < n_steps):
                    try:
                        event = self._datafeed.stream_next()
                        self._queue.put(event)
                        nstep += 1
                    except:  # pylint: disable=bare-except
                        # stop if not able to next event
                        self._active = False
                else:
                    break
            else:  # not empty
                try:
                    # call event handlers
                    if event.event_type in self._handlers:
                        for handler in self._handlers[event.event_type]:
                            handler(event)
                except Exception as exception:  # pylint: disable=broad-except
                    logging.error("Error %s", exception.args[0])

    def put(self, event: Event):
        """
        Put event in the queue; call from outside.

        Parameters
        ----------
            event : Event
                Event to put in the queue
        """
        self._queue.put(event)

    def register_handler(self, type_: str, handler):
        """
        Register handler/subscriber

        Parameters
        ----------
            type_ : str
                Event type

            handler : function
                Handler function
        """
        handler_list = self._handlers[type_]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister_handler(self, type_, handler):
        """
        Unregister handler/subscriber.

        Parameters
        ----------
            type_ : str
                Event type

            handler : function
                Handler function
        """
        handler_list = self._handlers[type_]
        if handler in handler_list:
            handler_list.remove(handler)
        if not handler_list:
            del self._handlers[type_]
