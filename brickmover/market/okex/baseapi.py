
from brickmover.market.marketbase  import MarketBase
import brickmover.market.okex.rest.api as restapi
from pprint import pprint

class BaseApi(MarketBase):
    def __init__(self,key='',secret='',exchange='',target='',base='',price_min_move=100000000,order_size_min=100000000):
        super(BaseApi, self).__init__('okex',target.upper(),base.upper(),price_min_move,order_size_min)  
        self.restapi = restapi.Api(apikey=key,secretkey=secret)
        self.symbol = target.lower() + '_' + base.lower()


    def GetMarketCode(self):
        return self.marketcode   
   
    #market info
    def GetTicker(self):
        response = self.restapi.ticker(symbol=self.symbol)
        ticker = response['ticker']
        return {'last':ticker['last']}
        
    def GetDepth(self):
        response = self.restapi.depth(symbol=self.symbol,size=5)
        depth = self.format_depth(response)
        return  depth 

    def GetTrades(self):
        response = self.restapi.trades(symbol=self.symbol)
        trades = []
        for item in response:
            trade = {}
            trade['price'] = item['price']
            trade['time'] = item['date_ms']
            trade['id'] = item['tid']
            trade['side'] =  item['type']
            trades.append(trade)
        return trades     

    #trade
    def Login(self):
        pass
    
    def Buy(self,price,quantity):
        response = self.restapi.trade(symbol=self.symbol,tradeType='buy',price=price,amount=quantity)
        order_id = -1
        try:
            order_id = response['order_id']
        except (KeyError):
            pass
        
        return order_id        
 
    def Sell(self,price,quantity):
        response = self.restapi.trade(symbol=self.symbol,tradeType='sell',price=price,amount=quantity)
        order_id = -1
        try:
            order_id = response['order_id']
        except (KeyError):
            pass
        
        return order_id
        
   
    def CancelOrder(self,orderid=None):
        response = self.restapi.cancelOrder(symbol=self.symbol,orderId=orderid)
        return response['result']  

    def GetOrder(self,orderid=None):
        response = self.restapi.orderinfo(symbol=self.symbol,orderId=orderid)
        #pprint(response)
        orders = response['orders']
        for order in orders:
            if order['order_id'] == orderid:
                orderinfo = {}
                orderinfo['price'] = order['price']
                orderinfo['quantity'] = order['amount']
                orderinfo['filled'] = order['deal_amount']
                orderinfo['symbol'] = order['symbol']
                orderinfo['side'] = order['type']   
        return orderinfo

    def GetOrders(self):
        response = self.restapi.orderinfo(symbol=self.symbol,orderId=-1)
        orderinfos = []
        orders = response['orders']
        for order in orders:
            orderinfo = {}
            orderinfo['price'] = order['price']
            orderinfo['quantity'] = order['amount']
            orderinfo['filled'] = order['deal_amount']
            orderinfo['symbol'] = order['symbol']
            orderinfo['side'] = order['type']  
            orderinfos.append(orderinfo)
        return orderinfos
    
    def GetAccount(self):
        response = self.restapi.userinfo()
        funds = response['info']['funds']
        free =  funds['free']
        freezed = funds['freezed']
        account = {}
        account[self.target] = {'free':float(free[self.target.lower()]),
                                'locked':float(freezed[self.target.lower()])} 
        
        account[self.base] = {'free':float(free[self.base.lower()]),
                                'locked':float(freezed[self.base.lower()])} 
        
        return account    



############### Util ####################    
    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'quantity': float(i[1])})
        return r

    def format_depth(self, depth):
        if(depth==None):
            return None
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}