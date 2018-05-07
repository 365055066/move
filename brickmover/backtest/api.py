

class ApiBS(object):

    def __init__(self,tquantity=0, bquantity=0,feeratio=0):
        
        #self.__long_position = 0
        #self.__long_average_price = None
        #self.__short_position = 0
        #self.__short_average_price = None 
        
        self.__tquantity = tquantity
        self.__bquantity = bquantity
        self.__init_tquantity = tquantity
        self.__init_bquantity = bquantity        
        self.__feeratio = feeratio
        
    def Buy(self,price,quantity):
        if self.__bquantity >= price*quantity:
            self.__bquantity -= price*quantity
            self.__tquantity += quantity*(1-self.__feeratio)
        
    def Sell(self,price,quantity):
        if self.__tquantity >= quantity:
            self.__tquantity -= quantity
            self.__bquantity +=  price*quantity*(1-self.__feeratio)
            
    def GetTargetQuantity(self):
        return self.__tquantity
    
    def GetBaseQuantity(self):
        return self.__bquantity

    def __str__(self):
        return 'tquantity:%s->%s bquantity=%s->%s: ' % (self.__init_tquantity,self.__tquantity, self.__init_bquantity,self.__bquantity)