
from brickmover.eventengie import Event
from brickmover.eventengie import EVENT_TYPE
from brickmover.eventengie import EVENT_DATA
from brickmover.eventengie import EVENT_LOGIN
from brickmover.eventengie import EVENT_DEPTH
from brickmover.eventengie import EVENT_TICK
from brickmover.eventengie import EVENT_ORDER
from brickmover.eventengie import EVENT_ACCOUNTINFO

class MarketBase(object):
    def __init__(self,exchange,symbol,currency,price_min_move,order_size_min,eventengie):
        self.exchange = exchange
        self.symbol = symbol
        self.currency = currency
        self.marketcode = self.exchange+ self.symbol +self.currency
        
        self.eventengie = eventengie

        self.price_min_move = price_min_move
        self.price_precision = 1/self.price_min_move
        self.order_size_min = order_size_min
        self.order_size_precision = 1/self.order_size_min
        
        self.symbol_reserved = 0
        self.symbol_available = 0
        self.currency_reserved = 0
        self.currency_available = 0
   
    #market info
    def GetTicker(self,isasync=False):
        pass
    
    def GetDepth(self,isasync=False):
        pass    

    def GetTrades(self,isasync=False):
        pass     
    
    def GetMarketCode(self):
        return self.marketcode
    
    #trade
    def Login(self,async=False):
        pass
    
    def Buy(self,price,quantity,isasync=False):
        pass
 
    def Sell(self,price,quantity,isasync=False):
        pass
   
    def CancelOrder(self,orderid=None,isasync=False):
        pass
    
    def GetOrders(self,orderid=None,isasync=False):
        pass
    
    def GetAccountInfo(self,isasync=True):
        pass    
    
    def SubscribeMarketInfo(self):
        pass
    
    def SubscribeTradeInfo(self):
        pass
        
    
    def _OnLogined(self,status):
        ev = Event(self.marketcode,{EVENT_TYPE:EVENT_LOGIN,
                                    EVENT_DATA:status})
        self.eventengie.putEvent(ev)        
    
    def _OnTick(self,tick):
        ev = Event(self.marketcode,{EVENT_TYPE:EVENT_TICK,
                                    EVENT_DATA:tick})
        self.eventengie.putEvent(ev)
    
    def _OnDepth(self,depth):
        ev = Event(self.marketcode,{EVENT_TYPE:EVENT_DEPTH,
                                    EVENT_DATA:depth})
        self.eventengie.putEvent(ev)
    
    #trade info stream
    def _OnOrder(self,order):
        '''
        status: new, suspended, partiallyFilled, filled, canceled, expired
        side:  sell or buy
        quantity: Order quantity
        price: Order price
        quantityExcuted: Cumulative executed quantity
        orderId: Unique identifier for Order as assigned by exchange
        clientOrderId: Unique identifier for Order as assigned by trader.
        updatetime: Datetime
        '''
        ev = Event(self.marketcode,{EVENT_TYPE:EVENT_ORDER,
                                    EVENT_DATA:order})
        self.eventengie.putEvent(ev)
  
    def _OnAccountInfo(self,accountinfo):
        ev = Event(self.marketcode,{EVENT_TYPE:EVENT_ACCOUNTINFO,
                                    EVENT_DATA:accountinfo})
        self.eventengie.putEvent(ev) 

    