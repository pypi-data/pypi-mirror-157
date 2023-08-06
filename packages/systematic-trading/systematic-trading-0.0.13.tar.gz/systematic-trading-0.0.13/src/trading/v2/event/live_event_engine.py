"""
Live event engine module.
"""
# pylint: disable=duplicate-code
from queue import Queue, Empty
from threading import Thread
from collections import defaultdict
import logging

from .event import Event

_logger = logging.getLogger(__name__)


class LiveEventEngine:
    """
    Event queue + a thread to dispatch events
    """

    def __init__(self):
        """
        Initialize dispatcher thread and handler function list
        """
        # if the dispatcher is active
        self._active = False

        # event queue
        self._queue = Queue()

        # dispatcher thread
        self._thread = Thread(target=self._run)

        # event handlers list, specific event --> handler dict
        self._handlers = defaultdict(list)

    def _run(self):
        """
        run dispatcher
        """
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                # call event handlers
                if event.event_type in self._handlers:
                    for handler in self._handlers[event.event_type]:
                        handler(event)
            except Empty:
                pass
            except Exception as exception:  # pylint: disable=broad-except
                _logger.error("Event %s, Error %s", event.event_type, str(exception))

    def start(self):
        """
        Start the dispatcher thread.
        """
        self._active = True
        self._thread.start()

    def stop(self):
        """
        Stop the dispatcher thread.

        Parameters
        ----------
            timer : bool
                If True, the dispatcher thread will be stopped.
        """
        self._active = False
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        Put event in the queue; call from outside.

        Parameters
        ----------
            event : Event
                Event to put in the queue.
        """
        self._queue.put(event)

    def register_handler(self, type_: str, handler) -> None:
        """
        Register handler/subscriber.

        Parameters
        ----------
            type_ : str
                Event type.

            handler : function
                Handler function.
        """
        handler_list = self._handlers[type_]

        if handler not in handler_list:
            handler_list.append(handler)

    def unregister_handler(self, type_: str, handler):
        """
        Unregister handler/subscriber.

        Parameters
        ----------
            type_ : str
                Event type.

            handler : function
                Handler function.
        """
        handler_list = self._handlers[type_]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            del self._handlers[type_]
