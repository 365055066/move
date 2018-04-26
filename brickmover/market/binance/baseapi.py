from brickmover.market.marketbase  import MarketBase
import brickmover.market.binance.rest.api as restapi

class BaseApi(MarketBase):
    def __init__(self,key='',secret='',exchange='',target='',base='',price_min_move=100000000,order_size_min=100000000):
        super(BaseApi, self).__init__(exchange,target,base,price_min_move,order_size_min)  
        self.restapi = restapi.Api(key,secret)
        self.symbol = target.upper() + base.upper()
        
    def GetTicker(self):
        response =self.restapi.get_symbol_ticker(symbol=self.symbol)
        print(response)
        pass
    
    def GetDepth(self):
        pass    

    def GetTrades(self):
        pass     

    #trade
    def Login(self):
        pass
    
    def Buy(self,price,quantitye):
        pass
 
    def Sell(self,price,quantity):
        pass
   
    def CancelOrder(self,orderid=None):
        pass
    
    def GetOrders(self,orderid=None):
        pass
    
    def GetAccountInfo(self):
        pass    

    