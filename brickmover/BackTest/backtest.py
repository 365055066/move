

class BackTestBS(object):

    def __init__(self,target=0, base=0):
        
        #self.__long_position = 0
        #self.__long_average_price = None
        #self.__short_position = 0
        #self.__short_average_price = None 
        
        self.__target = target
        self.__base = base
        self.__init_target = target
        self.__init_base = base        
        
    def B(self,p,q):
        if self.base >= p * q:
            self.base -= p * q
            self.target += q
        
    def S(self,p,q):
        if self.target >= q:
            self.target -= q
            self.base += p*q
            
    def GetTarget(self):
        return self.target
    
    def GetBase(self):
        return self.base

    