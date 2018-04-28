from brickmover.market.marketbase  import MarketBase
import brickmover.market.hitbtc.rest.api as restapi
from pprint import pprint
import time


class BaseApi(MarketBase):
    def __init__(self,key='',secret='',target='',base='',price_min_move=100000000,order_size_min=100000000):
        super(BaseApi, self).__init__('hitbtc',target=target.upper(),base=base.upper(),price_min_move=price_min_move,order_size_min=order_size_min)  
        self.restapi = restapi.Api(key,secret)
        self.symbol = target.upper() + base.upper()
        self.patialid = 0

######################## base api####################        
    #market info
    def GetTicker(self):
        try:
            response = self.restapi.get_symbol_ticker(symbol=self.symbol)
        except Exception:
            return None
        
        return {'last':float(response['last'])}
    
    def GetDepth(self,limit=5):
        try:
            response = self.restapi.get_order_book_for_symbol(symbol=self.symbol,limit=limit)
            depth = self.format_depth(response)
        except Exception:
            return None
            
        return depth
    
    def GetTrades(self,limit=5):
        response = self.restapi.get_trades_for_symbol(symbol=self.symbol,limit=limit)
        trades = []
        for item in response:
                trade = {}
                trade['price'] = item['price']
                trade['time'] = item['timestamp']
                trade['id'] = item['id']
                trade['side'] =  item['side']
                trade['quantity'] =  item['quantity']
                trades.append(trade)
        return trades     

    def Buy(self,price,quantity):
        try:
            response = self.restapi.post_order_for_symbol(symbol=self.symbol, side='buy', type="limit", quantity=quantity,price=price, 
                                                          #clientOrderId=self.genNextCliendid(), 
                                                          #timeInForce = 'GTC'
                                                          )
        except Exception:
            return None
        
        return response['clientOrderId']
 
    def Sell(self,price,quantity):
        try:
            response = self.restapi.post_order_for_symbol(symbol=self.symbol, side='sell', type="limit",  quantity=quantity,price=price, 
                                                          #clientOrderId=self.genNextCliendid(), 
                                                          #timeInForce = 'GTC'
                                                          )
        except Exception :
            return None
        
        return response['clientOrderId']
   
    def CancelOrder(self,orderid=None):
        try:
            response = self.restapi.delete_order_by_id(clientOrderId=orderid)
            if response['clientOrderId'] == orderid and response['status'] == 'canceled':
                return True
            else:
                return False
        except Exception :
            return False
        
        return False
        
    def GetOrder(self,orderid=None):
        try:
            response = self.restapi.get_order_by_id(clientOrderId=orderid)
            orderinfo = {}
            orderinfo['id'] = response['clientOrderId']
            orderinfo['price'] = response['price']
            orderinfo['quantity'] = response['quantity']
            orderinfo['filled'] = response['cumQuantity']
            orderinfo['symbol'] = response['symbol']
            orderinfo['side'] = response['side']
            orderinfo['status'] = response['status']  #new, suspended, partiallyFilled, filled, canceled, expired
        except Exception :
            return None  
        return orderinfo
           
    def GetOrders(self):
        try:
            response = self.restapi.get_all_orders_for_symbol(symbol=self.symbol)
            orderinfos = []
            for order in response:
                orderinfo = {}
                orderinfo['id'] = order['clientOrderId']
                orderinfo['price'] = order['price']
                orderinfo['quantity'] = order['quantity']
                orderinfo['filled'] = order['cumQuantity']
                orderinfo['symbol'] = order['symbol']
                orderinfo['side'] = order['side']
                orderinfo['status'] = order['status']  #new, suspended, partiallyFilled, filled, canceled, expired
                orderinfos.append(orderinfo)
        except Exception :
            return None
                           
        return orderinfos
    
    def GetAccount(self):
        try:
            response = self.restapi.get_trading_balance()
            account = {}
            for item in response:
                if item['currency'] == self.target:
                    account[self.target] = {'free':float(item['available']),
                                            'locked':float(item['reserved'])} 
                elif item['currency'] == self.base:
                    account[self.base] = {'free':float(item['available']),
                                          'locked':float(item['reserved'])} 
        except Exception :
            return None
        
        return account  



####################### Extend API ####################
    def GetKline(self,period=None,limit=100):
        response = self.restapi.get_candles_for_symbol(symbol=self.symbol,limit=limit,period=period)
        for item in response:
            line={}
            line['H']= item['max']
            line['L']= item['min']
            line['O']= item['open']
            line['C']= item['close']
            line['V']= item['volume']
            line['T']= item['timestamp']
        return response


####################### util #####################
    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x['price']), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i['price']), 'quantity': float(i['size'])})
        return r

    def format_depth(self, depth):
        if(depth==None):
            return None
        bids = self.sort_and_format(depth['bid'], True)
        asks = self.sort_and_format(depth['ask'], False)
        return {'asks': asks, 'bids': bids}    
    
    def genNextCliendid(self):
        self.patialid = (self.patialid+1)%10000
        cliendid = str(int(time.time())*10000 + self.patialid)        
        return  cliendid       
    
    
    
    
    
    