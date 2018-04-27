

class MarketBase(object):
    def __init__(self,exchange,target,base,price_min_move=100000000,order_size_min=100000000):
        self.exchange = exchange
        self.target = target
        self.base = base
        self.marketcode = self.exchange+ self.target +self.base
        
        self.price_min_move = price_min_move
        self.price_precision = 1/self.price_min_move
        self.order_size_min = order_size_min
        self.order_size_precision = 1/self.order_size_min
        
    def GetMarketCode(self):
        return self.marketcode   
  
    ################## Every market have Base API ############  
    def GetTicker(self):
        '''
        :returns: ticker or None
        '''
        pass
    
    def GetDepth(self):
        '''
        :returns: depth or None
        '''
        pass    

    def GetTrades(self):
        pass     

    def Buy(self,price,quantitye):
        '''
        :returns: order id,None if not
        '''
        pass
 
    def Sell(self,price,quantity):
        '''
        :returns: order id, None if not
        '''
        pass
   
    def CancelOrder(self,orderid=None):
        '''
        :returns: True or False
        '''
        pass

    def GetOrder(self,orderid=None):
        '''
        :returns: orderinfo or None
                orderinfo['id'] = 
                orderinfo['price'] 
                orderinfo['quantity'] 
                orderinfo['filled'] # filled quantity
                orderinfo['symbol'] 
                orderinfo['side']  # buy sell
                orderinfo['status']  #new, suspended, partiallyFilled, filled, canceled, expired
        '''
        pass   

    def GetOrders(self,orderid=None):
        '''
        :returns:orderinfo type {} or None
        '''
        pass
    
    def GetAccount(self):
        '''
        :returns:orderinfo Account {} or None
        '''
        pass    


    ############ Not every market have Extend API ##############
    def GetKline(self,period,limit):
        pass
    