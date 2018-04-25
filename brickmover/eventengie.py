from queue import Queue, Empty
from threading import Thread
from time import sleep
from collections import defaultdict

EVENT_TYPE = 'type'
EVENT_DATA = 'data'
EVENT_LOGIN = 'lonin'
EVENT_TIMER = 'timer'
EVENT_DEPTH = 'depth'
EVENT_TICK  = 'tick'
EVENT_ORDER = 'order'
EVENT_ACCOUNTINFO = 'accountinfo'

class EventEngine(object):

    def __init__(self):
        self.__queue = Queue()
        self.__active = False
        self.__thread = Thread(target = self.__run)   

        self.__timer = Thread(target = self.__runTimer)
        self.__timerActive = False
        self.__timerSleep = 15 #      
        
        self.__handlers = defaultdict(list)
        self.__generalHandlers = []        
        
    def __run(self):
        while self.__active == True:
            try:
                event = self.__queue.get(block = True, timeout = 1)  
                self.__process(event)
            except Empty:
                pass
            
    def __process(self, event):
        if event.type_ in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type_]]
                
        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]        
      
    def __runTimer(self):
        while self.__timerActive:
            event = Event(type_=EVENT_TIMER)
            self.putEvent(event)    
            sleep(self.__timerSleep)

    def start(self, timer=False,timersleep=15):
        self.__active = True
        self.__thread.start()
        if timer:
            self.__timerSleep=timersleep
            self.__timerActive = True
            self.__timer.start()

    def stop(self):
        self.__active = False
        self.__timerActive = False
        self.__timer.join()
        self.__thread.join()
            
    def register(self, type_, handler):
        handlerList = self.__handlers[type_]
        if handler not in handlerList:
            handlerList.append(handler)
            
    def unregister(self, type_, handler):
        handlerList = self.__handlers[type_]
        
        if handler in handlerList:
            handlerList.remove(handler)

        if not handlerList:
            del self.__handlers[type_]  
        
    def putEvent(self, event):
        self.__queue.put(event)

    def registerGeneralHandler(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)
            
    def unregisterGeneralHandler(self, handler):
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)

class Event:
    def __init__(self, type_=None, data_={}):
        self.type_ = type_
        self.data_ = data_


