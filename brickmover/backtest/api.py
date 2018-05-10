

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


class ApiLSb(object):
    def __init__(self,bquantity=0,feeratio=0):
        self.__long_position = 0
        self.__long_average_price = 0
        self.__short_position = 0
        self.__short_average_price = 0 
        
        self.__bquantity = bquantity
        self.__init_bquantity = bquantity        
        self.__feeratio = feeratio
        
    def Long(self,price,quantity):
        self.__long_average_price = (self.__long_position*self.__long_average_price + price*quantity) /(quantity+self.__long_position)
        self.__long_position += quantity
        self.__bquantity -= self.__feeratio * quantity

    def CloseLong(self,price,quantity):
        self.__bquantity +=  (price-self.__long_average_price)*quantity
        self.__long_position -= quantity
        if self.__long_position <= 0:
            self.__long_average_price = 0
        self.__bquantity -= self.__feeratio * quantity
         
    def Short(self,price,quantity):
        self.__short_average_price = (self.__short_position*self.__short_average_price + price*quantity)/(quantity+self.__short_position)
        self.__short_position += quantity
        self.__bquantity -= self.__feeratio * quantity
        
    def CloseShort(self,price,quantity):
        self.__bquantity += (self.__short_average_price - price)*quantity
        self.__short_position -= quantity
        if self.__short_position <= 0:
            self.__short_average_price = 0        
        self.__bquantity -= self.__feeratio * quantity

    def GetLongPosition(self):
        return self.__long_position
    
    def GetShortPosition(self):
        return self.__short_position
    
    def GetBaseQuantity(self):
        return self.__bquantity

    def GetFloatingBaseQuantity(self,clearprice):
        quantity = self.__bquantity
        if self.__long_position > 0:
            quantity +=  (clearprice-self.__long_average_price)*self.__long_position
        if self.__short_position > 0:
            quantity += (self.__short_average_price - clearprice)*self.__short_position
        return quantity

    def __str__(self):
        return 'bq=%s->%s,lp:%s,lavg:%s,sp:%s,savg:%s'%(self.__init_bquantity,self.__bquantity,self.__long_position,self.__long_average_price,self.__short_position,self.__short_average_price)

    
class ApiLSt(object):
    def __init__(self,tquantity=0,feeratio=0):
        self.__long_position = 0
        self.__long_average_price = 0
        self.__short_position = 0
        self.__short_average_price = 0 
        
        self.__tquantity = tquantity
        self.__init_tquantity = tquantity        
        self.__feeratio = feeratio
        
    def Long(self,price,quantity):
        self.__long_average_price = (self.__long_position*self.__long_average_price + price*quantity) /(quantity+self.__long_position)
        self.__long_position += quantity
        self.__tquantity -= self.__feeratio * quantity

    def CloseLong(self,price,quantity):
        self.__tquantity +=  (price-self.__long_average_price)*quantity/price
        self.__long_position -= quantity
        if self.__long_position <= 0:
            self.__long_average_price = 0
        self.__tquantity -= self.__feeratio * quantity
         
    def Short(self,price,quantity):
        self.__short_average_price = (self.__short_position*self.__short_average_price + price*quantity)/(quantity+self.__short_position)
        self.__short_position += quantity
        self.__tquantity -= self.__feeratio * quantity
        
    def CloseShort(self,price,quantity):
        self.__tquantity += (self.__short_average_price - price)*quantity/price
        self.__short_position -= quantity
        if self.__short_position <= 0:
            self.__short_average_price = 0
            
        self.__tquantity -= self.__feeratio * quantity
    
    def GetLongPosition(self):
        return self.__long_position
    
    def GetShortPosition(self):
        return self.__short_position
    
    def GetTargetQuantity(self):
        return self.__tquantity

    def GetFloatingTargetQuantity(self,clearprice):
        quantity = self.__tquantity
        if self.__long_position > 0:
            quantity +=  (clearprice-self.__long_average_price)*self.__long_position/clearprice
        if self.__short_position > 0:
            quantity += (self.__short_average_price - clearprice)*self.__short_position/clearprice
        return quantity

    def __str__(self):
        return 'tq=%s->%s,lp:%s,lavg:%s,sp:%s,savg:%s'%(self.__init_tquantity,self.__tquantity,self.__long_position,self.__long_average_price,self.__short_position,self.__short_average_price)
 
 
    