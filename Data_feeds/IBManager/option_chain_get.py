
from ib_insync import *
import pandas as pd
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')

from datetime import datetime

port = int(config.get('main', 'ibkr_port'))

# TWs 7497, IBGW 4001
ib = IB().connect('127.0.0.1',  port)


def get_chain(ticker,exp_list):
    exps = {}
    df = pd.DataFrame(columns=['strike','kind','close','last'])
    for i in exp_list:
        cds = ib.reqContractDetails(Option(ticker, i, exchange='SMART'))
        options = [cd.contract for cd in cds]
        tickers = [t for i in range(0, len(options), 100) for t in ib.reqTickers(*options[i:i + 100])]

        for x in tickers:
            # print(x)
            df = df.append({'strike':x.contract.strike,'kind':x.contract.right,'close':x.close,'last':x.last,'bid':x.bid,'ask':x.ask,'mid':(x.bid+x.ask)/2,'volume':x.volume},ignore_index=True)
            exps[i] = df

    return exps


def get_individual(ticker,exp,strike,kind):
    cds = ib.reqContractDetails(Option(ticker, exp,strike,kind ,exchange='SMART'))
    options = [cd.contract for cd in cds]
    tickers = [t for i in range(0, len(options), 100) for t in ib.reqTickers(*options[i:i + 100])]

    con = {'strike':tickers[0].contract.strike,'kind':tickers[0].contract.right,'close':tickers[0].close,'last':tickers[0].last,'bid':tickers[0].bid,'ask':tickers[0].ask,'volume':tickers[0].volume}
    return con



# t0 = datetime.now()

# print(get_individual('AMD','20200828','80','C'))



# print(get_chain('AMD',['20200828','20200904']))

# print(datetime.now()-t0)