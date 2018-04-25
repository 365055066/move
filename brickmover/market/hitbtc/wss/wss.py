"""Connector Base class."""

# pylint: disable=too-many-arguments

# Import Built-Ins
import logging
from queue import Queue
from threading import Thread, Timer
import multiprocessing as mp

import json
import time
import ssl

# Import Third-Party
import websocket

# Import home-grown

# Init Logging Facilities
class WebSocketConnector:
    """Websocket Connection Thread.

    Inspired heavily by ekulyk's PythonPusherClient Connection Class
    https://github.com/ekulyk/PythonPusherClient/blob/master/pusherclient/connection.py

    Data received is available by calling WebSocketConnection.recv()
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments,unused-argument

    def __init__(self, url, timeout=None, q_maxsize=None, reconnect_interval=None, log_level=None):
        """Initialize a WebSocketConnector Instance.

        :param url: websocket address, defaults to v2 websocket.
        :param timeout: timeout for connection; defaults to 10s
        :param reconnect_interval: interval at which to try reconnecting;
                                   defaults to 10s.
        :param log_level: logging level for the connection Logger. Defaults to
                          logging.INFO.
        :param args: args for Thread.__init__()
        :param kwargs: kwargs for Thread.__ini__()
        """
        # Queue used to pass data up to Node
        self.q = Queue(maxsize=q_maxsize or 100)

        # Connection Settings
        self.url = url
        self.conn = None

        # Connection Handling Attributes
        self._is_connected = False
        self.reconnect_required = True  #False
        self.reconnect_interval = reconnect_interval if reconnect_interval else 1

        # Set up history of sent commands for re-subscription
        self.history = []

        # Tracks Websocket Connection
        self.connection_timer = None
        self.connection_timeout = timeout if timeout else 10

        if log_level == logging.DEBUG:
            websocket.enableTrace(True)

    def stop(self):
        """Wrap around disconnect()."""
        self.disconnect()

    def disconnect(self):
        """Disconnect from the websocket connection and joins the Thread."""
        self.reconnect_required = False
        self._is_connected = False
        if self.conn:
            self.conn.close()

    def reconnect(self):
        """Issue a reconnection by setting the reconnect_required event."""
        # Reconnect attempt at self.reconnect_interval
        self.reconnect_required = True
        self._is_connected = False
        if self.conn:
            self.conn.close()

    def _connect(self):
        """Create a websocket connection.

        Automatically reconnects connection if it was severed unintentionally.
        """
        self.conn = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        self.conn.run_forever(sslopt=sslopt_ca_certs)

    def run(self):
        """Run the main method of thread."""
        self._connect()

    def _on_message(self, ws, message):
        """Handle and pass received data to the appropriate handlers.

        Resets timers for time-out countdown and logs exceptions during parsing.

        All messages are time-stamped

        :param ws: Websocket obj
        :param message: received data as bytes
        :return:
        """
        pass

    def _on_close(self, ws, *args):
        """Log the close and stop the time-out countdown.

        Execute when the connection is closed.

        :param ws: Websocket obj
        :param *args: additional arguments
        """
        logging.info("Connection closed")
        
        if self.reconnect_required:
            logging.info("try reconnect")
            time.sleep(self.reconnect_interval)
            self._connect()

    def _on_open(self, ws):
        """Log connection status, set Events for _connect(), start timers and send a test ping.

        Execute on opening a new connection.

        If the connection was previously severed unintentionally, it re-subscribes
        to the channels by executing the commands found in self.history, in
        chronological order.

        :param ws: Webscoket obj
        """
        logging.info("Connection opened")
        self._is_connected = True

        if self.reconnect_required:
            pass

    def _on_error(self, ws, error):
        """Log the error, reset the self._is_connected flag and issue a reconnect.

        Callback executed on connection errors.

        Issued by setting self.reconnect_required.

        :param ws: Websocket obj
        :param error: Error message
        """
        logging.info("Connection Error - %s", error)
        self._is_connected = False

    def send(self, data):
        """Send the given Payload to the API via the websocket connection.

        Furthermore adds the sent payload to self.history.

        :param data: data to be sent
        :return:
        """
        if self._is_connected:
            payload = json.dumps(data)
            #self.history.append(data)
            self.conn.send(payload)
        else:
            logging.error("Cannot send payload! Connection not established!")

    def recv(self, block=True, timeout=None):
        """Wrap for self.q.get().

        :param block: Whether or not to make the call to this method block
        :param timeout: Value in seconds which determines a timeout for get()
        :return:
        """
        return self.q.get(block, timeout)


class WebSocketConnectorThread(WebSocketConnector, Thread):
    """Thread-based WebsocketConnector."""

    def __init__(self, url, timeout=None, q_maxsize=None, reconnect_interval=None, log_level=None,
                 **kwargs):
        """Initialize the instance."""
        super(WebSocketConnectorThread, self).__init__(url, timeout=timeout, q_maxsize=q_maxsize,
                                                       reconnect_interval=reconnect_interval,
                                                       log_level=log_level)
        Thread.__init__(self, **kwargs)
        self.daemon = True

    def disconnect(self):
        """Disconnect from the websocket and join thread."""
        super(WebSocketConnectorThread, self).disconnect()
        Thread.join(self, timeout=1)

