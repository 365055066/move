"""HitBTC Connector which pre-formats incoming data to the CTS standard."""

import logging
import time
import json
import hmac
import hashlib
from threading import Timer
from collections import defaultdict

from brickmover.market.hitbtc.wss.wss import WebSocketConnectorThread
from brickmover.market.hitbtc.wss.utils import response_types


class HitBTCConnector(WebSocketConnectorThread):
    """Class to pre-process HitBTC data, before putting it on the internal queue.

    Data on the queue is available as a 3-item-tuple by default.
    
    Response items on the queue are formatted as:
        ('Response', (request, response))
    
    'Success' indicates a successful response and 'Failure' a failed one. 
    ``request`` is the original payload sent by the
    client and ``response`` the related response object from the server.
    
    Stream items on the queue are formatted as:
        (method, params)

    You can disable extraction and handling by passing 'raw=True' on instantiation. Note that this
    will also turn off recording of sent requests, as well all logging activity.
    """

    def __init__(self, url=None, raw=None, stdout_only=False, silent=False, **conn_ops):
        """Initialize a HitBTCConnector instance."""
        url = url or 'wss://api.hitbtc.com/api/2/ws'
        super(HitBTCConnector, self).__init__(url, **conn_ops)
        self.requests = {}
        self.raw = raw
        self.logged_in = False
        self.silent = silent
        self.stdout_only = stdout_only
        self.ajustid=0
        
        self.relogin = True
        self.key = None
        self.secret = None
        self.basic = None

    def put(self, item, block=False, timeout=None):
        """Place the given item on the internal q."""
        if not self.stdout_only:
            self.q.put(item, block, timeout)

    def echo(self, msg):
        """Print message to stdout if ``silent`` isn't True."""
        if not self.silent:
            logging.info(msg)

    def _on_message(self, ws, message):
        """Handle and pass received data to the appropriate handlers."""
        if not self.raw:
            decoded_message = json.loads(message)
            if 'jsonrpc' in decoded_message:
                if 'result' in decoded_message or 'error' in decoded_message:
                    self._handle_response(decoded_message)
                else:
                    try:
                        method = decoded_message['method']
                        params = decoded_message['params']
                    except Exception as e:
                        logging.error(decoded_message)
                        return
                    self._handle_stream(method, params)
        else:
            self.put(message)
            
    def _on_open(self, ws):
        super(WebSocketConnectorThread,self)._on_open(ws)
        if self.relogin is True and self.key is not None:
            self.authenticate(self.key, self.secret, self.basic)

    def _handle_response(self, response):
        """
        Handle JSONRPC response objects.

        Acts as a pre-sorting function and determines whether or not the response is an error
        message, or a response to a succesful request.
        """
        try:
            i_d = response['id']
        except KeyError as e:
            logging.exception(e)
            logging.error("An expected Response ID was not found in %s", response)
            raise

        try:
            request = self.requests.pop(i_d)
        except KeyError as e:
            logging.exception(e)
            logging.error("Could not find Request relating to Response object %s", response)
            raise

        self._handle_request_response(request, response)
        if 'error' in response:
            self._handle_error(request, response)

    def _handle_error(self, request, response):
        err_message = "{code} - {message} - {description}!".format(**response['error'])
        err_message += " Related Request: %r" % request
        logging.error(err_message)

    def _handle_request_response(self, request, response):
        self.put(('Response', (request, response)))

    def _handle_stream(self, method, params):
        self.put((method, params))

    def send(self, method, custom_id=None, **params):
        """
        Send the given Payload to the API via the websocket connection.

        :param method: JSONRPC method to call
        :param custom_id: custom ID to identify response messages relating to this request
        :param kwargs: payload parameters as key=value pairs
        """
        if not self._is_connected:
            self.echo("Cannot Send payload - Connection not established!")
            return
        
        self.ajustid =(self.ajustid+1)%1000000
        payload = {'method': method, 'params': params, 'id': custom_id or (int(time.time() )*1000000 + self.ajustid)}
        if not self.raw:
            self.requests[payload['id']] = payload
            
        #logging.info("Sending: %s", payload)
        self.conn.send(json.dumps(payload))

    def authenticate(self, key, secret, basic=False, custom_nonce=None):
        """Login to the HitBTC Websocket API using the given public and secret API keys."""
        if self.relogin is True:
            self.key = key
            self.secret = secret
            self.basic = basic
        
        if basic:
            algo = 'BASIC'
            skey = secret
            payload = {'sKey': skey}
        else:
            algo = 'HS256'
            nonce = custom_nonce or str(round(time.time() * 1000))
            signature = hmac.new(secret.encode('UTF-8'), nonce.encode('UTF-8'), hashlib.sha256).hexdigest()
            payload = {'nonce': nonce, 'signature': signature}

        payload['algo'] = algo
        payload['pKey'] = key
        self.send('login', **payload)
