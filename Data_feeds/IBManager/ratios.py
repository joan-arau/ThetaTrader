from ib.ext.Contract import Contract
from ib.opt import ibConnection
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')


from datetime import datetime
port = int(config.get('main', 'ibkr_port'))

from time import sleep
import pandas as pd
pd.set_option('display.max_columns', 500)


# https://interactivebrokers.github.io/tws-api/fundamental_ratios_tags.html

# Class used to download data from IB API
class Downloader(object):
    tickType47value = ''
    #field4price = ''

    def __init__(self):
        self.tws = ibConnection('localhost', port,20)
        self.tws.register(self.tickPriceHandler, 'TickString')
        self.tws.connect()
        self._reqId = 1003 # current request id

    def tickPriceHandler(self,msg):
        if msg.tickType == 47:    # tickType=47
            self.tickType47value = msg.value
            #print('[debug]', msg)

    def requestData(self,contract):
        self.tws.reqMarketDataType(4)
        self.tws.reqMktData(self._reqId, contract, "233, 236, 258", False)  #"233, 236, 258",
        self._reqId+=1

    def cancelData(self):
        #self.tws.cancelMktData(1003)
        self.tws.disconnect()


def get_ratios(stocks,cols):
    dl = Downloader()
    c = Contract()
    #Create empty list to store data
    l = []
    # Loop over list of stocks
    idx = 0
    for x in stocks:
        idx += 1
        for _ in range(5):

            c.m_symbol = x
            c.m_secType = 'STK'
            c.m_exchange = 'SMART'
            c.m_currency = 'USD'
            # sleep(1)
            dl.requestData(c)
            sleep(1)
            m0 = str(x)
            m = dl.tickType47value
            sleep(1)

            if dl.tickType47value:


                    row = []
                    row.append(m0)
                    row.append(m)

                    dl.cancelData()
                    # sleep(0.5)



                    r = row[1].split(';')

                    dic = {}
                    dic['Symbol'] = row[0]
                    for i in r:
                        item = i.split('=')

                        if len(item)>1:

                            dic[item[0]]=item[1]
                            if item[1] == '-99999.99' :
                                dic[item[0]] = 0

                    l.append(dic)
                    print(row[0],' Added ', idx,'/',len(stocks))

                    break


            dl.cancelData()
            # sleep(0.5)

    if cols != None:
        df = pd.DataFrame(l)[cols]
    #print(df)
    return df



# df = get_ratios(['AAL','WYNN','SIX','MGM','MAR','HLT','WYND'],['Symbol','APENORM','AROAPCT','AROIPCT','BETA','DIVGRPCT','EPSTRENDGR','PR52WKPCT','PRICE2BK','QCURRATIO','QLTD2EQ','QPR2REV','QQUICKRATI','QTOTD2EQ','REVTRENDGR','TTMGROSMGN','TTMINTCOV','TTMNIPEREM','TTMOPMGN','TTMPAYRAT','YIELD','YLD5YAVG'])
# print(df)

# df = float(get_ratios(['AAPL'],['YIELD']).iloc[0])
#
# print(df)