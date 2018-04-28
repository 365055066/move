from brickmover.market.marketbase  import MarketBase
import brickmover.market.binance.rest.api as restapi

class BaseApi(MarketBase):
    def __init__(self,key='',secret='',target='',base='',price_min_move=100000000,order_size_min=100000000):
        super(BaseApi, self).__init__('binance',target=target.upper(),base=base.upper(),price_min_move=price_min_move,order_size_min=order_size_min)  
        self.restapi = restapi.Api(key,secret)
        self.symbol = target.upper() + base.upper()
 
 
############### API ####################       
    def GetTicker(self):
        response =self.restapi.get_symbol_ticker(symbol=self.symbol)
        return {'last':float(response['price'])}
        pass
    
    def GetDepth(self,limit=5):
        response = self.restapi.get_order_book(symbol=self.symbol,limit=limit)
        #print(response)
        return self.format_depth(response)
        pass    

    def GetTrades(self,limit=5):
        pass     

    def Buy(self,price,quantity):
        response = self.restapi.order_limit_buy(symbol=self.symbol,price=price,quantity=quantity)
        print(response)
        pass
 
    def Sell(self,price,quantity):
        pass
   
    def CancelOrder(self,orderid=None):
        pass
    
    def GetOrder(self,orderid=None):
        pass    
    
    def GetOrders(self):
        pass
    
    def GetAccount(self):
        response = self.restapi.get_account()
        balances =  response['balances']
        account = {}
        for item in balances:
            asset = item['asset']
            if  asset == self.target or asset == self.base:
                account[asset] = {'free':float(item['free']),'locked':float(item['locked'])} 
                
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
    