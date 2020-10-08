# # Interactive Brokers functions to import data
#
from configparser import ConfigParser

config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



port = int(config.get('main', 'ibkr_port'))
#
# def tws_time(): # request time to "wake-up" IB's API
#
#     from datetime import datetime
#     from threading import Thread
#     import time
#
#     from ibapi.client import EClient
#     from ibapi.wrapper import EWrapper
#     from ibapi.common import TickerId
#
#
#     class ib_class(EWrapper, EClient):
#
#         def __init__(self, addr, port, client_id):
#             EClient. __init__(self, self)
#
#             self.connect(addr, port, client_id) # Connect to TWS
#             thread = Thread(target=self.run)  # Launch the client thread
#             thread.start()
#
#         def currentTime(self, cur_time):
#             t = datetime.fromtimestamp(cur_time)
#             print('Current TWS date/time: {}\n'.format(t))
#
#         def error(self, reqId:TickerId, errorCode:int, errorString:str):
#             if reqId > -1:
#                 print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " , errorString)
#
#     ib_api = ib_class('127.0.0.1', port, 0)
#     ib_api.reqCurrentTime() # associated callback: currentTime
#     time.sleep(0.5)
#     ib_api.disconnect()
#
#
# def read_positions(): #read all accounts positions and return DataFrame with information
#
#     from ibapi.client import EClient
#     from ibapi.wrapper import EWrapper
#     from ibapi.common import TickerId
#     from threading import Thread
#
#     import pandas as pd
#     import time
#
#     class ib_class(EWrapper, EClient):
#
#         def __init__(self, addr, port, client_id):
#             EClient.__init__(self, self)
#
#             self.connect(addr, port, client_id) # Connect to TWS
#             thread = Thread(target=self.run)  # Launch the client thread
#             thread.start()
#
#             self.all_positions = pd.DataFrame([], columns = ['Account','Symbol', 'Quantity', 'Average Cost', 'Sec Type','Strike','right','exp'])
#
#         def error(self, reqId:TickerId, errorCode:int, errorString:str):
#             if reqId > -1:
#                 print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " , errorString)
#
#         def position(self, account, contract, pos, avgCost):
#             index = str(account)+str(contract.symbol)
#
#             self.all_positions.loc[index]= account, contract.symbol, pos, avgCost, contract.secType,contract.strike,contract.right,contract.lastTradeDateOrContractMonth
#
#     ib_api = ib_class("127.0.0.1", port, 10)
#     ib_api.reqPositions() # associated callback: position
#     print("Waiting for IB's API response for accounts positions requests...\n")
#     time.sleep(5)
#     current_positions = ib_api.all_positions
#     current_positions =current_positions.reset_index(drop=True)
#     ib_api.disconnect()
#
#     return(current_positions)
#
#
# def read_navs(): #read all accounts NAVs
#
#     from ibapi.client import EClient
#     from ibapi.wrapper import EWrapper
#     from ibapi.common import TickerId
#     from threading import Thread
#
#     import pandas as pd
#     import time
#
#     class ib_class(EWrapper, EClient):
#
#         def __init__(self, addr, port, client_id):
#             EClient.__init__(self, self)
#
#             self.connect(addr, port, client_id) # Connect to TWS
#             thread = Thread(target=self.run)  # Launch the client thread
#             thread.start()
#
#             self.all_accounts = pd.DataFrame([], columns = ['reqId','Account', 'Tag', 'Value' , 'Currency'])
#
#         def error(self, reqId:TickerId, errorCode:int, errorString:str):
#             if reqId > -1:
#                 print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " , errorString)
#
#         def accountSummary(self, reqId, account, tag, value, currency):
#             index = str(account)
#             self.all_accounts.loc[index]=reqId, account, tag, value, currency
#
#     ib_api = ib_class("127.0.0.1", port, 10)
#     ib_api.reqAccountSummary(0,"All","NetLiquidation") # associated callback: accountSummary
#     print("Waiting for IB's API response for NAVs requests...\n")
#     time.sleep(3.0)
#     current_nav = ib_api.all_accounts
#     ib_api.disconnect()
#
#     return(current_nav)
#
#
# print(read_positions().sort_values('Symbol'))


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import *
from ibapi.contract import *

# import os
import pandas as pd

class TestApp(EClient, EWrapper):
    posns = []


    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId:int):
        # print("id", orderId)
        # print("starting program")
        self.reqPositions()

    def error(self, reqId:TickerId, errorCode:int, errorString:str):
        print("Error: ", reqId, "", errorCode, "", errorString)

    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        self.posns.append((account, contract.symbol, position, avgCost, contract.secType,contract.strike,contract.right,contract.lastTradeDateOrContractMonth))
        # print(contract.symbol, position)

    def positionEnd(self):
        print(self.isConnected())
        self.disconnect()
        # self.waitOnUpdate(timeout=0.1)
        print(self.isConnected())
        print('ACD Disconnected')
        self.df = pd.DataFrame(self.posns,columns = ['Account','Symbol', 'Quantity', 'apx', 'Sec Type','Strike','right','exp'])


    def return_pos(self):
        return self.df

def read_positions():
    app = TestApp()
    app.connect("127.0.0.1", port, 20)
    app.run()
    # app.disconnect()
    return app.return_pos()

# print(read_positions())