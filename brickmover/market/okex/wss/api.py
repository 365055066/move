

from threading import Thread

import websocket
import time
import json
import logging

from brickmover.market.marketbase import MarketBase

class Api(MarketBase):
    
    def __init__(self,key='',secret='', symbol='',currency='',price_min_move=0.00000001,order_size_min=0.00000001,eventengie=None,needdepthlenth=5):
        super().__init__('okex',symbol.upper(),currency.upper(),price_min_move,order_size_min,eventengie)

        self.key= key 
        self.secret =secret 
        
        self.code = symbol.upper() + currency.upper()
        self.__thread = Thread(target = self.__run)  
        self.__thread.start() 
        self.__handlers =  {  }   
        self.__last_ping_time = time.time()
        
        self.__connectserver()
        self.__reconncet = False

    def __connectserver(self):
        url = "wss://real.okex.com:10441/websocket"
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(url,
                                    on_message = self.__on_message,
                                    on_error = self.__on_error,
                                    on_close = self.__on_close)
        ws.on_open = self.__on_open
        ws.run_forever()
        self.__reconncet = False

    def __on_open(self,ws):
        #ws.send("{'event':'addChannel','channel':'ok_sub_spot_eos_usdt_depth_10','parameters':{'api_key':'69b2c63a-cd6a-4e7a-98cf-b75ff09c79e9','sign':'2CDEFF643461E8114692C7B80A809D5A'}}")
        self.send("{'event':'addChannel','channel':'ok_sub_spot_eos_usdt_depth_10'}")
    
    def __on_message(self,ws,evt):
        pass
         
    def __on_error(self,ws,evt):
        print(evt)
        self.__reconncet = True
    
    def __on_close(self,ws):
        print('disconnected')
        print('reconncet..')
        time.sleep(3)
        self.__connectserver()
    
    def __run(self):
        while True:
            time.sleep(1)
        pass


        
    
