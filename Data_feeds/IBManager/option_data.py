from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import SetOfString
from ibapi.common import SetOfFloat
from threading import Timer
from ibapi.contract import Contract

from configparser import ConfigParser

import csv

temp_file = '/Users/joan/PycharmProjects/ThetaTrader/db/temp.csv'

config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



port = int(config.get('main', 'ibkr_port'))

from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', port, clientId=11)
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

    def __init__(self,ticker,conid):
        self.ticker = ticker
        self.conid= conid
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):

        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):

        self.start()
        # pass

    def securityDefinitionOptionParameter(self, reqId:int, exchange:str, underlyingConId:int, tradingClass:str, multiplier:str, expirations:SetOfString, strikes:SetOfFloat):
        # print("SecurityDefinitionOptionParameter.", "ReqId:", reqId, "Exchange:", exchange, "Underlying conId:", underlyingConId, "TradingClass:", tradingClass, "Multiplier:", multiplier, "Expirations:", expirations, "Strikes:", str(strikes),"\n")
        dets = {"ReqId":reqId, "Exchange":exchange, "Underlying conId":underlyingConId, "TradingClass": tradingClass, "Multiplier": multiplier, "Expirations": expirations,"Strikes": str(strikes)}
        # print(dets['Expirations'])
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

def main(ticker):

    ticker= ticker
    conid = ib.qualifyContracts(Stock(ticker, 'SMART', 'USD'))[0].conId
    app = TestApp(ticker= ticker,conid=conid)
    app.nextOrderId = 0
    # TWs 7497, IBGW 4001
    app.connect("127.0.0.1", port, 0)





    Timer(4, app.stop).start()
    app.run()

if __name__ == "__main__":
    main('AMD')