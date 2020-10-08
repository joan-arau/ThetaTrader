from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum



def create_contract(symbol, sec_type, exch, prim_exch, curr):
    """Create a Contract object defining what will
    be purchased, at which exchange and in which currency.

    symbol - The ticker symbol for the contract
    sec_type - The security type for the contract ('STK' is 'stock')
    exch - The exchange to carry out the contract on
    prim_exch - The primary exchange to carry out the contract on
    curr - The currency in which to purchase the contract"""
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract


class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)

    def error(selfself, reqId, errorCode, errorString):
        print("Error:",reqId, " ", errorCode," ", errorString)

    def tickPrice(self,reqId, tickType, price, attrib):
        print("Tick Price Ticker Id:", reqId,"tickType:", TickTypeEnum.to_str(tickType), 'Price:', price,end=" ")

    def tickSize(selfself, reqId, tickType, size):
        print("Ticksize ticker Id:", reqId,"tickType:",TickTypeEnum.to_str(tickType),"Size:", size)

def main():
    app = TestApp()
    app.connect('127.0.0.1',4001,0)

    contract = create_contract('AAPL', 'STK', 'SMART','NASDAQ', 'USD')


    app.reqMarketDataType(4)
    app.reqMktData(1, contract, "",False,False,[])
    app.run()
    app.disconnect()
    print('MD Disconnected')

if __name__ == "__main__":
    main()