from pprint import pformat

import requests


class HitbtcClientRest:
    def __init__(self, key: str, secret: str, url: str = 'https://api.hitbtc.com/api/2'):
        try:
            self.session = requests.session()
            self.session.auth = (key, secret)
        except Exception as e:
            raise
        
        self.url = {}
        try:
            self.url['base'] = url
        except Exception as e:
            raise

    # Public API Methods
    def get_symbols(self) -> dict:
        return self.get_symbol()

    def get_symbol(self, symbol: str = None) -> dict:
        path = '/public/symbol/'
        if symbol is None:
            endpoint = ''
        else:
            endpoint = symbol

        return self.get(locals())

    def get_currencies(self) -> dict:
        return self.get_currency()

    def get_currency(self, currency: str = None) -> dict:
        path = '/public/currency'
        if currency is None:
            endpoint = ''
        else:
            endpoint = currency

        return self.get(locals())

    def get_ticker(self) -> dict:
        return self.get_symbol_ticker()

    def get_symbol_ticker(self, symbol: str = None) -> dict:
        path = '/public/ticker/'
        if symbol is None:
            endpoint = ''
        else:
            endpoint = symbol

        return self.get(locals())

    def get_trades_for_symbol(self, symbol: str, sort: str = None, by: str = None, from_type: str = None, till: str = None, limit: str = None) -> dict:
        path = '/public/trades/'
        if symbol is None:
            raise Exception('Argument symbol must be specified')
        else:
            endpoint = symbol

        return self.get(locals())

    def get_order_book_for_symbol(self, symbol: str, limit: int = None) -> dict:
        path = '/public/orderbook/'
        if symbol is None:
            raise Exception('Argument symbol must be specified')
        else:
            endpoint = symbol

        return self.get(locals())

    def get_candles_for_symbol(self, symbol: str, limit: int = None, period: str = None) -> dict:
        path = '/public/candles/'
        if symbol is None:
            raise Exception('Argument symbol must be specified')
        else:
            endpoint = symbol

        return self.get(locals())

    # Trading API Methods

    def get_all_orders(self) -> dict:
        return self.get_order_book_for_symbol()

    def get_all_orders_for_symbol(self, symbol: str = None) -> dict:
        path = '/order'
        return self.get(locals())

    def post_order_for_symbol(self, symbol: str, side: str, quantity: str, clientOrderId: str = None, type: str = None, timeInForce: str = None, price: str = None,
                              stopPrice: str = None, expireTime: str = None, strictValidate: bool = True) -> dict:
        path = '/order'
        if None in [symbol, side, quantity]:
            raise Exception('Arguments symbol, side, quantity must be specified')

        return self.post(locals())

    def delete_all_orders_for_symbol(self, symbol: str) -> dict:
        path = '/order'
        if symbol is None:
            raise Exception('Argument symbol must be specified')

        return self.delete(locals())

    def get_order_by_id(self, clientOrderId: str, wait: str = None) -> dict:
        path = '/order/'
        if clientOrderId is None:
            raise Exception('Argument clientOrderId must be specified')
        else:
            endpoint = clientOrderId

        return self.get(locals())

    def put_order_for_symbol(self, symbol: str, side: str, clientOrderId: str, timeInForce: str, quantity: str, type: str = None, price: str = None,
                             stopPrice: str = None, expireTime: str = None, strictValidate: bool = True) -> dict:
        path = '/order/'
        if None in [clientOrderId, symbol, side, quantity, timeInForce]:
            raise Exception('Arguments clientOrderId, symbol, side, quantity, timeInForce must be specified')
        else:
            endpoint = clientOrderId

        return self.put(locals())

    def delete_order_by_id(self, clientOrderId: str) -> dict:
        path = '/order/'
        if clientOrderId is None:
            raise Exception('Argument clientOrderId must be specified')
        else:
            endpoint = clientOrderId

        return self.delete(locals())

    def patch_order_by_id(self, clientOrderId: str) -> dict:
        path = '/order/'
        if clientOrderId is None:
            raise Exception('Argument clientOrderId must be specified')
        else:
            endpoint = clientOrderId

        return self.patch(locals())

    def get_trading_balance(self) -> list:
        path = '/trading/balance'
        return self.get(locals())

    def get_trading_fee(self, symbol) -> dict:
        path = '/trading/fee/'
        if symbol is None:
            raise Exception('Argument symbol must be specified')
        else:
            endpoint = symbol
        return self.get(locals())

    # Trading History API Methods

    # Account API Methods
    def get_account_balance(self):
        path = '/account/balance'
        return self.get(locals())

    def get_account_transactions(self, transaction_id: str = None) -> dict:
        path = '/account/transactions'
        if transaction_id is not None:
            path += '/%s' % transaction_id
        return self.get(locals())

    def get_account_transaction_by_id(self, transaction_id) -> dict:
        return self.get_account_transactions(transaction_id)


    # API Helper Methods
    def get(self, params: dict) -> dict:
        return self.__call('get', params)

    def patch(self, params: dict) -> dict:
        return self.__call('patch', params)

    def put(self, params: dict) -> dict:
        return self.__call('put', params)

    def post(self, params: dict) -> dict:
        return self.__call('post', params)

    def delete(self, params: dict) -> dict:
        return self.__call('delete', params)

    def __call(self, method: str, params: dict) -> dict:
        if 'endpoint' not in params:
            params['endpoint'] = ''
        if 'from_type' in params:
            params['from'] = params['from_type']
            del params['from_type']

        data = {}

        for key in params.keys():
            if params[key] is not None and key not in ['path', 'endpoint', 'self']:
                data[key] = params[key]

        if hasattr(self.session, method):
            try:
                #print("%s%s%s" % (self.url['base'], params['path'], params['endpoint']))
                #print('data=%s' % pformat(data))
                try:
                    r = getattr(self.session, method)(url="%s%s%s" % (self.url['base'], params['path'], params['endpoint']), params=data).json()
                except Exception as e:
                    raise
                if 'error' in r:
                    raise Exception('API Error: %s' % r)
                return r
            except Exception as e:
                raise
        return {}  # For Code Annotations
