

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
        
        #self.target_reserved = 0
        #self.target_available = 0
        #self.base_reserved = 0
        #self.base_available = 0
   
    def GetMarketCode(self):
        return self.marketcode   
   
    #market info
    def GetTicker(self):
        pass
    
    def GetDepth(self):
        pass    

    def GetTrades(self):
        pass     

    #trade
    def Login(self):
        pass
    
    def Buy(self,price,quantitye):
        '''
        return: orderid
        '''
        pass
 
    def Sell(self,price,quantity):
        '''
        return: orderid
        '''
        pass
   
    def CancelOrder(self,orderid=None):
        '''
        return: True or False
        '''
        pass

    def GetOrder(self,orderid=None):
        pass   

    def GetOrders(self,orderid=None):
        pass
    
    def GetAccount(self):
        pass    




    