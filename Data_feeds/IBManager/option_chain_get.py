from datetime import datetime
import ib_insync
from ib_insync import *

from ibapi.contract import Contract
import pandas as pd
from configparser import ConfigParser
import pytz
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')
import signal
from datetime import datetime, time
from Data_feeds.IBManager.option_data import main as get_exps
from random import randint
import csv
tmp_file = '/Users/joan/PycharmProjects/ThetaTrader/db/temp.csv'
def in_between(now, start=time(9,30), end=time(16)):

    day = datetime.today().weekday()

    print(day)
    if start <= now < end and day != 5 and day != 6:
        return 1
    else:

        return 2

    # else: # over midnight e.g., 23:30-04:15
    #     return start <= now or now < end


timeZ_Ny = pytz.timezone('America/New_York')
data_type = in_between(datetime.now(timeZ_Ny).time())


# print(data_type)



port = int(config.get('main', 'ibkr_port'))

# TWs 7497, IBGW 4001



# def get_chain(ticker,exp_list):
#     exps = {}
#     df = pd.DataFrame(columns=['strike','kind','close','last'])
#     for i in exp_list:
#         cds = ib.reqContractDetails(Option(ticker, i, exchange='SMART'))
#         options = [cd.contract for cd in cds]
#         tickers = [t for i in range(0, len(options), 100) for t in ib.reqTickers(*options[i:i + 100])]
#
#         for x in tickers:
#             # print(x)
#             df = df.append({'strike':x.contract.strike,'kind':x.contract.right,'close':x.close,'last':x.last,'bid':x.bid,'ask':x.ask,'mid':(x.bid+x.ask)/2,'volume':x.volume},ignore_index=True)
#             exps[i] = df
#
#     return exps



def get_chain(ticker,exp_list = None):
    ib = IB().connect('127.0.0.1', port, clientId=20)
    exps = {}
    df = pd.DataFrame(columns=['strike','kind','close','last'])
    ib.reqMarketDataType(data_type)

    if exp_list == None :
        get_exps(ticker)
        with open(tmp_file, newline='') as f:
            reader = csv.reader(f)
            exp_list = list(reader)[0]
            # exp_list = list((datetime.strftime(i, "%m%d%Y") for i in exp_list))
    print(exp_list)
    for i in exp_list:
        cds = ib.reqContractDetails(Option(ticker, i, exchange='SMART'))
        # print(cds)
        options = [cd.contract for cd in cds]
        # print(options)
        l = []
        for x in options:
            # print(x)
            contract = Option(ticker, i, x.strike, x.right, "SMART", currency="USD")
            # print(contract)
            snapshot = ib.reqMktData(contract, "", True, False)

            l.append([x.strike,x.right,snapshot])
            # print(snapshot)

        while util.isNan(snapshot.bid):
            ib.sleep()
        for ii in l:
            # print(ii)
            df = df.append({'strike':float(ii[0]),'kind':ii[1],'close':ii[2].close,'last':ii[2].last,'bid':ii[2].bid,'ask':ii[2].ask,'mid':(ii[2].bid+ii[2].ask)/2,'volume':ii[2].volume},ignore_index=True)
            exps[i] = df
    ib.disconnect()
    return exps


# def get_individual(ticker,exp,strike,kind):
#     cds = ib.reqContractDetails(Option(ticker, exp,strike,kind ,exchange='SMART'))
#     options = [cd.contract for cd in cds]
#     tickers = [t for i in range(0, len(options), 100) for t in ib.reqTickers(*options[i:i + 100])]
#
#     con = {'strike':tickers[0].contract.strike,'kind':tickers[0].contract.right,'close':tickers[0].close,'last':tickers[0].last,'bid':tickers[0].bid,'ask':tickers[0].ask,'volume':tickers[0].volume}
#     return con
def handler(signum, frame):

    raise Exception("TimeOut")
def get_individual(ticker = None,exp = None,strike = None,kind = None,conId = None):
    ib = IB().connect('127.0.0.1', port, clientId=20)
    ib.reqMarketDataType(data_type)

    if conId == None:
        con = Option(ticker, exp, strike, kind, "SMART", currency='USD')
        # print(con)
        snapshot = ib.reqMktData(con, "", False, False)
        while util.isNan(snapshot.bid):
            ib.sleep()
        # contract = Contract(conId = conId,)
    else:

        ib.reqMarketDataType(3)
        for exchange in ['SMART','DTB']:
            # print(exchange)
            con = ib_insync.contract.Contract(conId=int(conId),exchange = exchange)
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(5)
            try:
                snapshot = ib.reqMktData(con, "", False, False)
                while util.isNan(snapshot.bid):
                    ib.sleep()
                break
            except Exception:
                pass
    signal.alarm(0)

    # print(ib.isConnected())
    ib.disconnect()
    ib.waitOnUpdate(timeout=0.1)
    # print(ib.isConnected())
    # print('ODG Disconnected')
    # time.sleep(1)
    # print(snapshot)
    return {'strike': strike, 'kind': kind, 'close': snapshot.close, 'last': snapshot.last, 'bid': snapshot.bid, 'ask': snapshot.ask, 'volume': snapshot.volume}


    # except:
    #     try:
    #
    #         snapshot = ib.reqMktData(con, "", False, False)
    #         while util.isNan(snapshot.bid):
    #             ib.sleep()
    #         print(ib.isConnected())
    #         ib.disconnect()
    #         ib.waitOnUpdate(timeout=0.1)
    #         print(ib.isConnected())
    #         print('ODG Disconnected')
    #         # time.sleep(1)
    #         print(snapshot)
    #         return {'strike': strike, 'kind': kind, 'close': snapshot.close, 'last': snapshot.last, 'bid': snapshot.bid,
    #                 'ask': snapshot.ask, 'volume': snapshot.volume}
    #
    #     except:
    #
    #
    #         return {'strike': None, 'kind': None, 'close': None, 'last': None, 'bid': None, 'ask': None, 'volume': None}


#
# t0 = datetime.now()
# print(get_individual(conId = 259069531))
# print(datetime.now()-t0)
#
# t0 = datetime.now()
# print(get_individual('AMD',"20201224",80,'C'))
# print(datetime.now()-t0)
#
# t0 = datetime.now()
# print(get_individual('AAPL',"20210416",120,'C'))
# print(datetime.now()-t0)

#
# t0 = datetime.now()
# print(get_chain('AAPL'))
# print(datetime.now()-t0)

# print(datetime.now()-t0)