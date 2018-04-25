from brickmover.market.marketbase import MarketBase
from threading import Thread

import brickmover.market.hitbtc.wss.api.Api as Hitbtcwssapi

import time
import queue
import copy
import logging

class hitbtcmarket(MarketBase):
    
    def __init__(self,key='',secret='', symbol='',currency='',eventengie=None,needdepthlenth=5):
        super().__init__('hitbtc',symbol.upper(),currency.upper(),eventengie)

        self.key= key 
        self.secret =secret 
        
        self.code = symbol.upper() + currency.upper()
        self.hitbtapi  = Hitbtcwssapi()
        self.__thread = Thread(target = self.__run)  
        self.__thread.start() 
        self.__handlers =  {  
                'snapshotOrderbook':self.__onSnapshotOrderbook,  
                'updateOrderbook':self.__onUpdateOrderbook,
                'Response':self.__onResponse,
                'report':self.__onReport,
                'activeOrders':self.__onActiveOrders,
                'ticker':self.__onTicker,
            }   
        
        self.depthsequence=0
        self.asks = []
        self.bids = []
        self.maxdepthlenth = 50
        self.needdepthlenth= needdepthlenth
        
        self.patialid=0
    
    def __run(self):
        self.hitbtapi.start()  # start the websocket connection
        time.sleep(6)  # Give the socket some time to connect
        
        self.hitbtapi.login(key=self.key,secret=self.secret)
        
        while True:
            try:
                data = self.hitbtapi.recv()
            except queue.Empty:
                continue
            #print("...")
            #print(data)
            method = data[0]
            handller = self.__handlers.get(method)
            if handller != None:
                handller(data[1])

    def __onResponse(self,data):
        handlers =  {  
                'login':self.__onLogin,  
                'getTradingBalance':self.__onGetTradingBalance,
            } 
        try:
            method = data[0]['method']
        except Exception as e:
            logging.error(e)
            return
            
        handler = handlers.get(method)
        if handler != None:
            handler(data)
    
    def __onReport(self,data):
        #data = data[2]
        if data['symbol']==self.code:
            orderdata={}
            orderdata['clientOrderId'] = data['clientOrderId']
            orderdata['orderId'] = data['id']
            orderdata['side'] = data['side']
            orderdata['price'] = float(data['price'])
            orderdata['quantity'] = float(data['quantity'])
            orderdata['quantityExcuted'] = float(data['cumQuantity'])
            orderdata['status'] = data['status']
            orderdata['updatetime'] = data['updatedAt']
            orderdata['isResidual'] = False
            if 'tradeFee' in data:
                orderdata['tradeFee'] = float(data['tradeFee'])
            self.onOrder(orderdata)
    
    def __onActiveOrders(self,data):
        for order in data:
            if order['symbol'] == self.code :
                orderdata={}
                orderdata['clientOrderId'] = order['clientOrderId']
                orderdata['orderId'] = order['id']
                orderdata['side'] = order['side']
                orderdata['price'] = float(order['price'])
                orderdata['quantity'] = float(order['quantity'])
                orderdata['quantityExcuted'] = float(order['cumQuantity'])
                orderdata['status'] = order['status']
                orderdata['updatetime'] = order['updatedAt']
                orderdata['isResidual'] = True
                if 'tradeFee' in order:
                    orderdata['tradeFee'] = float(order['tradeFee'])
                self.onOrder(orderdata)    
                
         
    def __onTicker(self,data): 
        data['ask'] = float(data['ask'] )
        data['bid'] = float(data['bid'] )
        self.onTick(data)
    
        
    def __onLogin(self,data):
        result = data[1]['result']
        if result is True:
            self.onLogined(True)
            #self.hitbtapi.subscribe_book(symbol=self.code) 
            self.hitbtapi.subscribe_reports()
            self.hitbtapi.request_balance() 
            self.hitbtapi.subscribe_ticker(symbol=self.code) 
        else:
            self.onLogined(False)
        

    def __onSnapshotOrderbook(self,data):
        depth = data
        if depth['symbol'] == self.code:
            asks = depth["ask"][0:self.maxdepthlenth]
            bids = depth["bid"][0:self.maxdepthlenth]
            #asks.sort(key=lambda x: float(x["price"]), reverse=False)
            #bids.sort(key=lambda x: float(x["price"]), reverse=True)
            
            self.asks = []
            for i in asks:
                self.asks.append({'price': float(i["price"]), 'size': float(i["size"])})
                
            self.bids = []
            for i in bids:
                self.bids.append({'price': float(i["price"]), 'size': float(i["size"])})
            
            self.depthsequence= depth["sequence"]
            
            
    def __onUpdateOrderbook(self,data): 
        depth = data
        if depth['symbol'] == self.code:
            if  depth["sequence"] - self.depthsequence == 1:
                asks_o = depth["ask"][0:self.maxdepthlenth]
                bids_o = depth["bid"][0:self.maxdepthlenth]
                #asks.sort(key=lambda x: float(x["price"]), reverse=False)
                #bids.sort(key=lambda x: float(x["price"]), reverse=True)
                asks = []
                for i in asks_o:
                    asks.append({'price': float(i["price"]), 'size': float(i["size"])})
                self.asks= self.__updateOrderbook(self.asks,asks,True)
            
                bids = []
                for i in bids_o:
                    bids.append({'price': float(i["price"]), 'size': float(i["size"])})
                self.bids = self.__updateOrderbook(self.bids,bids,False)
     
                if self.asks[0]['price']<=self.bids[0]['price'] :
                    self.__onOrderBookError()

                self.depthsequence= depth["sequence"]
                
                self.onDepth({'asks': copy.deepcopy( self.asks[0:self.needdepthlenth] ),
                              'bids': copy.deepcopy( self.bids[0:self.needdepthlenth] )})
                
            else:
                self.__onOrderBookError()
            
    def __updateOrderbookItem(self,orderbook,updateitem):
        if len(orderbook)==0:
                orderbook.append(updateitem)
        else:
            if orderbook[-1] ['price']==updateitem['price'] :
                if updateitem['size'] == 0 or  orderbook[-1]['size']==0:
                    del orderbook[-1]
                else:
                    orderbook[-1]['size']=  orderbook[-1]['size']+ updateitem['size']                  
            else:
                orderbook.append(updateitem)

    def __updateOrderbook(self,book1,book2,increase=True):
        count1 = len(book1)
        count2 = len(book2)
        catlen = count1+count2
        r = []
        for i in range(0,catlen):
            if count1>0 and count2 > 0:
                item1 = book1[0]
                item2 = book2[0]
                if increase:
                    if item1['price']<=item2['price'] :
                        updateitem = item1
                        movelist = book1
                        count1 -=1
                    else:
                        updateitem = item2
                        movelist = book2
                        count2 -=1
                else:
                    if item1['price']>=item2['price'] :
                        updateitem = item1
                        movelist = book1
                        count1 -=1
                    else:
                        updateitem = item2
                        movelist = book2
                        count2 -=1
                
                self.__updateOrderbookItem(r,updateitem)
                del movelist[0] 
            elif count1 > 0:
                updateitem= book1[0]  
                self.__updateOrderbookItem(r,updateitem)
                count1 -=1
                del book1[0]  
            elif count2 > 0:
                updateitem = book2[0] 
                self.__updateOrderbookItem(r,updateitem) 
                count2 -=1
                del book2[0]   
        return r[0:self.maxdepthlenth]

    def __onOrderBookError(self):
        logging.error("onOrderBookError")
        self.onDepth(None)
        self.hitbtapi.subscribe_book(cancel=True, symbol=self.code)
        time.sleep(1)
        self.hitbtapi.subscribe_book(symbol=self.code)

    def __onGetTradingBalance(self,data):
        result = data[1]['result']
        for item in result:
            if item['currency'] == self.symbol:
                self.symbol_reserved = float(item['reserved'])
                self.symbol_available = float(item['available'])
            elif item['currency'] == self.currency:
                self.currency_reserved = float(item['reserved'])
                self.currency_available = float(item['available'])
        self.onAccountInfo({'symbol_reserved':copy.deepcopy(self.symbol_reserved),
                            'symbol_available':copy.deepcopy(self.symbol_available),
                            'currency_reserved':copy.deepcopy(self.currency_reserved),
                            'currency_available':copy.deepcopy(self.currency_available),
                            })
        
    def sendOrder(self,side,price,quantity,cliendid=None):
        if cliendid == None:
            self.patialid = (self.patialid+1)%1000000
            randomid = str(int(time.time())*1000000 + self.patialid)
        
        self.hitbtapi.place_order(
                clientOrderId =  cliendid or randomid ,
                symbol=self.code,
                side=side,
                type='limit',
                quantity=quantity,
                price=price)
        
    def cancelOrder(self,orderid=None,clientOrderId=None):
        if clientOrderId is not None:
            self.hitbtapi.cancel_order(clientOrderId=clientOrderId)
        else:
            raise Exception('hitbtc cancelOrder clientOrderId == None')
    
    def getAccountInfo(self):
        self.hitbtapi.request_balance() 
        
    
