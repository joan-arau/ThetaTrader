from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import SetOfString
from ibapi.common import SetOfFloat
from threading import Timer
from ibapi.contract import Contract

from configparser import ConfigParser
from random import randint
import csv

temp_file = '/Users/joan/PycharmProjects/ThetaTrader/db/temp.csv'

config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



port = int(config.get('main', 'ibkr_port'))

from ib_insync import *

ib = IB()
# ib.connect('127.0.0.1', port, clientId=20)
# amd = Stock('AMD', 'SMART', 'USD')
#
# # cds = ib.reqContractDetails(amd)
#
# cds = ib.qualifyContracts(amd)[0].conId
#
# print(cds[0].conId)


# print(create_contract('AAPL', 'STK', 'SMART','NASDAQ', 'USD'))
# breakpoint()

class TestApp(EWrapper, EClient):

    def __init__(self,ticker):
        # ib.connect('127.0.0.1', port, clientId=30)
        self.ticker = ticker
        self.conid= ib.qualifyContracts(Stock(ticker, 'SMART', 'USD'))[0].conId
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):

        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):

        self.start()
        # pass

    def securityDefinitionOptionParameter(self, reqId:int, exchange:str, underlyingConId:int, tradingClass:str, multiplier:str, expirations:SetOfString, strikes:SetOfFloat):
        # print("SecurityDefinitionOptionParameter.", "ReqId:", reqId, "Exchange:", exchange, "Underlying conId:", underlyingConId, "TradingClass:", tradingClass, "Multiplier:", multiplier, "Expirations:", expirations, "Strikes:", str(strikes),"\n")
        dets = {"ReqId":reqId, "Exchange":exchange, "Underlying conId":underlyingConId, "TradingClass": tradingClass, "Multiplier": multiplier, "Expirations": expirations,"Strikes": str(strikes)}
        print(dets['Expirations'])
        with open(temp_file, 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(sorted(dets['Expirations']))

        return dets

    def securityDefinitionOptionParameterEnd(self, reqId:int):

        print("SecurityDefinitionOptionParameterEnd. ReqId:", reqId)

    def start(self):

        # 265598 is the conId (contract ID) for AAPL Nasdaq stock
        return self.reqSecDefOptParams(1, self.ticker, "", "STK", self.conid)

    def stop(self):

        self.done = True

        self.disconnect()
        # self.waitOnUpdate(timeout=0.1)


def main(ticker):

    ticker= ticker
    iB = ib.connect("127.0.0.1", port, 20)
    app = TestApp(ticker=ticker)

    # conid = ib.qualifyContracts(Stock(ticker, 'SMART', 'USD'))[0].conId

    app.nextOrderId = 0
    # TWs 7497, IBGW 4001






    Timer(4, app.stop).start()
    app.run()
    print(iB.isConnected())
    iB.disconnect()
    iB.waitOnUpdate(timeout=0.1)
    print(iB.isConnected())
    print('OD Disconnected')

if __name__ == "__main__":
    main('AMD')