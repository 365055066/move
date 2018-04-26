from brickmover.market.marketbase  import MarketBase
import brickmover.market.hitbtc.rest.api as restapi
from pprint import pprint
import time


class BaseApi(MarketBase):
    def __init__(self,key='',secret='',target='',base='',price_min_move=100000000,order_size_min=100000000):
        super(BaseApi, self).__init__('hitbtc',target.upper(),base.upper(),price_min_move,order_size_min)  
        self.restapi = restapi.Api(key,secret)
        self.symbol = target.upper() + base.upper()
        self.patialid = 0
        
    #market info
    def GetTicker(self):
        response = self.restapi.get_symbol_ticker(symbol=self.symbol)
        return {'last':float(response['last'])}
    
    def GetDepth(self):
        response = self.restapi.get_order_book_for_symbol(symbol=self.symbol,limit=5)
        depth = self.format_depth(response)
        return depth
    
    def GetTrades(self):
        pass     

    #trade
    def Login(self):
        pass
    
    def Buy(self,price,quantity):
        #response = self.restapi.post_order_for_symbol(symbol=self.symbol, side='buy', type="limit", 
        #                                              quantity=quantity,price=price, 
        #                                              clientOrderId=self.genNextCliendid(),   timeInForce = 'GTC')
        
        response = self.restapi.new_order(client_order_id=self.genNextCliendid(), symbol_code=self.symbol, side='buy', quantity=quantity, price=price)
        pprint(response)
 
    def Sell(self,price,quantity):
        pass
   
    def CancelOrder(self,orderid=None):
        response = self.restapi.delete_order_by_id(clientOrderId=orderid)
        pprint(response)

    def GetOrder(self,orderid=None):
        pass   

    def GetOrders(self,orderid=None):
        pass
    
    def GetAccount(self):
        response = self.restapi.get_trading_balance()
        account = {}
        for item in response:
            if item['currency'] == self.target:
                account[self.target] = {'free':float(item['available']),
                                        'locked':float(item['reserved'])} 
            elif item['currency'] == self.base:
                account[self.base] = {'free':float(item['available']),
                                      'locked':float(item['reserved'])} 
        return account  




    
######################################################
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
    
    
    
    
    
    