

from threading import Thread

import websocket
import time
import json
import logging

from brickmover.market.marketbase import MarketBase

class Baseapi(MarketBase):
    
    def __init__(self,key='',secret='', symbol='',currency='',price_min_move=0.00000001,order_size_min=0.00000001,eventengie=None,needdepthlenth=5):
        super().__init__('okex',symbol.upper(),currency.upper(),price_min_move,order_size_min,eventengie)

        self.key= key 
        self.secret =secret 
        self.code = symbol.upper() + currency.upper()


    
