
from brickmover.market.marketbase  import MarketBase
import brickmover.market.okex.rest.api as restapi
import brickmover.market.okex.rest.apifuture as restapifuture
from pprint import pprint
import logging
import dateparser

def sort_and_format(l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'quantity': float(i[1])})
        return r

def format_depth(depth):
        if(depth==None):
            return None
        bids = sort_and_format(depth['bids'], True)
        asks = sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}

ORDER_STATUS_MAP= {-1:'canceled',
                       0:'new',
                       1:'partiallyFilled',
                       2:'filled',
                       4:'suspended',
                       5:'suspended'}
        
class BaseApi(MarketBase):
    

    def __init__(self,key='',secret='',target='',base='',price_min_move=100000000,order_size_min=100000000):
        super(BaseApi, self).__init__(exchange='okex',target=target.upper(),base=base.upper(),price_min_move=price_min_move,order_size_min=order_size_min)  
        self.restapi = restapi.Api(apikey=key,secretkey=secret)
        self.symbol = target.lower() + '_' + base.lower()

    #market info
    def GetTicker(self):
        response=None
        try: 
            response = self.restapi.ticker(symbol=self.symbol)
            ticker = response['ticker']
            return {'last':ticker['last']}
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None

    def GetDepth(self,limit=5):
        response=None
        try:
            response = self.restapi.depth(symbol=self.symbol,size=limit)
            depth = format_depth(response)
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        
        return  depth 

    def GetTrades(self):
        response=None
        try:
            response = self.restapi.trades(symbol=self.symbol)
            trades = []
            for item in response:
                trade = {}
                trade['price'] = item['price']
                trade['time'] = item['date_ms']
                trade['id'] = item['tid']
                trade['side'] =  item['type']
                trade['quantity'] =  item['amount']
                trades.append(trade)
            return trades   
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None

    def Buy(self,price,quantity):
        response=None
        try:
            response = self.restapi.trade(symbol=self.symbol,tradeType='buy',price=price,amount=quantity)
            order_id = -1
            order_id = response['order_id']
            return order_id
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
     
    def Sell(self,price,quantity):
        response=None
        try:
            response = self.restapi.trade(symbol=self.symbol,tradeType='sell',price=price,amount=quantity)
            order_id = -1
            order_id = response['order_id']
            return order_id
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        

    def CancelOrder(self,orderid=None):
        response=None
        try:
            response = self.restapi.cancelOrder(symbol=self.symbol,orderId=orderid)
            return response['result']  
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None 

    def GetOrder(self,orderid=None):
        response=None
        try:
            response = self.restapi.orderinfo(symbol=self.symbol,orderId=orderid)
            orders = response['orders']
            for order in orders:
                if order['order_id'] == orderid:
                    orderinfo = {}
                    orderinfo['id'] = order['order_id']
                    orderinfo['price'] = order['price']
                    orderinfo['quantity'] = order['amount']
                    orderinfo['filled'] = order['deal_amount']
                    orderinfo['symbol'] = order['symbol']
                    orderinfo['side'] = order['type']  
                    orderinfo['status'] = ORDER_STATUS_MAP[order['status']]        
            return orderinfo
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        
    def GetOrders(self):
        response=None
        try:
            response = self.restapi.orderinfo(symbol=self.symbol,orderId=-1)
            orderinfos = []
            orders = response['orders']
            for order in orders:
                orderinfo = {}
                orderinfo['id'] = order['order_id']
                orderinfo['price'] = order['price']
                orderinfo['quantity'] = order['amount']
                orderinfo['filled'] = order['deal_amount']
                orderinfo['symbol'] = order['symbol']
                orderinfo['side'] = order['type']  
                orderinfo['status'] = ORDER_STATUS_MAP[order['status']]
                orderinfos.append(orderinfo)
            return orderinfos
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        
    def GetAccount(self):
        response=None
        try:
            response = self.restapi.userinfo()
            funds = response['info']['funds']
            free =  funds['free']
            freezed = funds['freezed']
            account = {}
            account[self.target] = {'free':float(free[self.target.lower()]),
                                    'locked':float(freezed[self.target.lower()])} 
            
            account[self.base] = {'free':float(free[self.base.lower()]),
                                    'locked':float(freezed[self.base.lower()])} 
            
            return account 
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None  



    
    
class BaseApiFuture(MarketBase):
    
    FUTURE_ORDER_SIDE_MAP = {1:'long',2:'short',3:'close-long',4:'close-short'}
    
    
    def __init__(self,key='',secret='',target='',base='',contract_type=None,price_min_move=100000000,order_size_min=100000000):
        '''
        :contractType this_week , next_week , quarter 
        '''
        super(BaseApiFuture, self).__init__(exchange='okexfuture',target=target.upper(),base=base.upper(),contract_type=contract_type, price_min_move=price_min_move,order_size_min=order_size_min)  
        self.restapifuture = restapifuture.Apifuture(apikey=key,secretkey=secret)
        self.symbol = target.lower() + '_' + base.lower()
        self.contract_type = contract_type
    
    def GetTicker(self):
        response=None
        try:
            response = self.restapifuture.future_ticker(symbol=self.symbol,contractType=self.contract_type)
            return {'last':response['ticker']['last']}
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
            
    def GetDepth(self,limit=5):
        response=None
        try:
            response = self.restapifuture.future_depth(symbol=self.symbol,contractType=self.contract_type, size=limit)
            depth = format_depth(response)
        except  Exception as e:
            logging.error(response)
            logging.error(e)
            return None
    
        return  depth         


    def GetTrades(self):
        response=None
        try:
            response =  self.restapifuture.future_trades(symbol=self.symbol,contractType=self.contract_type)   
            pprint(response)
            trades = []
            for item in response:
                trade = {}
                trade['price'] = item['price']
                trade['time'] = item['date_ms']
                trade['id'] = item['tid']
                trade['side'] =  item['type']
                trade['quantity'] =  item['amount']
                trades.append(trade)
                return trades   
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        
    def Long(self,price,quantity):
        response=None
        try:
            response =  self.restapifuture.future_trade(symbol=self.symbol,contractType=self.contract_type,
                                                        price=price,amount=quantity,tradeType='1',matchPrice='0')
            return response['order_id']
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None

    def CloseLong(self,price,quantity):
        response=None
        try:
            response =  self.restapifuture.future_trade(symbol=self.symbol,contractType=self.contract_type,
                                                        price=price,amount=quantity,tradeType='3',matchPrice='0')
            return response['order_id']
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None
    
    def Short(self,price,quantity):
        response=None
        try:
            response =  self.restapifuture.future_trade(symbol=self.symbol,contractType=self.contract_type,
                                                        price=price,amount=quantity,tradeType='2',matchPrice='0')
            return response['order_id']
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None

    def CloseShort(self,price,quantity):
        response=None
        try:
            response =  self.restapifuture.future_trade(symbol=self.symbol,contractType=self.contract_type,
                                                        price=price,amount=quantity,tradeType='4',matchPrice='0')
            return response['order_id']
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None


    def GetOrder(self,orderid=None):
        response=None
        try:
            response =  self.restapifuture.future_orderinfo(symbol=self.symbol,contractType=self.contract_type,orderId=orderid)
            orders = response['orders']
            pprint(orders)
            for order in orders:
                    if str(order['order_id']) == orderid:
                        orderinfo = {}
                        orderinfo['id'] = order['order_id']
                        orderinfo['price'] = order['price']
                        orderinfo['quantity'] = order['amount']
                        orderinfo['filled'] = order['deal_amount']
                        orderinfo['symbol'] = order['symbol']
                        orderinfo['side'] = self.FUTURE_ORDER_SIDE_MAP[order['type']]  
                        orderinfo['status'] = ORDER_STATUS_MAP[order['status']]        
                        return orderinfo
            return None
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None

    def GetOrders(self):
        response=None
        try:
            currentPage = 1
            orderinfos = []
            while True:
                response =  self.restapifuture.future_orderinfo(symbol=self.symbol,contractType=self.contract_type,orderId=-1,status=1,currentPage=1,pageLength=50)
                orders = response['orders']
                for order in orders:
                    orderinfo = {}
                    orderinfo['id'] = order['order_id']
                    orderinfo['price'] = order['price']
                    orderinfo['quantity'] = order['amount']
                    orderinfo['filled'] = order['deal_amount']
                    orderinfo['symbol'] = order['symbol']
                    orderinfo['side'] = order['type']  
                    orderinfo['status'] = ORDER_STATUS_MAP[order['status']]
                    orderinfos.append(orderinfo)
                if len(orders) < 50:
                    break   
                else:
                    currentPage +=1
                    
            return orderinfos
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None


    def CancelOrder(self,orderid=None):
        response=None
        try:
            response = self.restapifuture.future_cancel(symbol=self.symbol,contractType=self.contract_type,orderId=orderid)
            return response['result']  
        except  Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        
    def GetAccount(self):
        response=None
        try:
            response = self.restapifuture.future_userinfo_4fix()
            info = response['info']
            account = info[self.target.lower()]
            # balance:Óà¶î
            # rights:È¨Òæ
            # 'contracts': [...]
            return account 
        except  Exception as e:
            logging.error(response)
            logging.error(e)
            return None
        
    ######################
    def GetKline(self,period,limit=0):
        PERIOD_MAP = {'M1':'1min', 'M3':'3min', 'M5':'5min', 'M15':'15min', 'M30':'30min', 
                      'H1':'1hour', 'H4':'4hour','H6':'6hour', 'H12':'12hour', 'D1':'D1', 'D7':'D7', "1M":"1M"}
        lines=[]
        try:
            response =  self.restapifuture.future_kline(symbol=self.symbol,contractType=self.contract_type,period=PERIOD_MAP[period],size=limit)   
            for item in response:
                    line={}
                    line['T']= item[0]#dateparser.parse(str(item[0]))
                    line['O']= item[1]
                    line['H']= item[2]
                    line['L']= item[3]
                    line['C']= item[4]
                    line['V']= item[5]
                    lines.append(line)
            return lines
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None        
       
    def GetPosition(self):  
        try:
            response =  self.restapifuture.future_position_4fix(symbol=self.symbol,contractType=self.contract_type,type1=1)
            holding=response['holding']
            position = {}
            symbol = self.symbol
            if self.base.lower() == 'usdt':
                symbol = self.target.lower() + '_usd'
            for item in holding:
                if item['symbol'] == symbol:
                    
                    position['long_position'] = item['buy_amount']
                    position['long_available'] = item['buy_available']
                    position['long_average_price'] = item['buy_price_avg']  
                    position['short_position'] = item['sell_amount']
                    position['short_available'] = item['sell_available']
                    position['short_average_price'] = item['sell_price_avg']
            return position
        
        except Exception as e:
            logging.error(response)
            logging.error(e)
            return None     
        
        
        