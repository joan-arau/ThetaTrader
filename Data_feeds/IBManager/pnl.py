# import ibapi
# from ibapi.client import EClient
# from ibapi.wrapper import EWrapper
# from ibapi.common import *
# from ibapi.contract import *
#
# import pandas as pd
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# import collections
# import time
#
#
# class TestApp(EClient, EWrapper):
#     accts = []
#     orderId = 0
#     posns = collections.defaultdict(list)
#     start = time.time()
#
#
#     def __init__(self):
#         EClient.__init__(self, self)
#         self.dic_l = []
#
#     def error(self, reqId: TickerId, errorCode: int, errorString: str):
#         if (reqId > -1):
#             # ignore many 2150 Invalid position trade derived value
#             if (errorCode == 2150): return
#             print("Error:", reqId, errorCode, errorString)
#         else:
#             print("Info: ", errorCode, errorString)
#
#     def managedAccounts(self, accountsList: str):
#         # the accounts are sent when a connection is made
#         # only needed to reqPosns for sub acct
#         self.accts = accountsList.split(",")  # probably just 1
#         print("accts", self.accts)
#
#     def nextValidId(self, orderId: int):
#         # this is called when a connection is made
#         self.orderId = orderId
#
#         # to make sure the version is >= min 9.73.06, server > ~127?
#         print(ibapi.VERSION, self.serverVersion())
#
#         # use this as a signal to start making requests
#         self.reqPositions()
#
#     def position(self, account: str, contract: Contract, position: float, avgCost: float):
#         self.posns["account"].append(account)
#         self.posns["conId"].append(contract.conId)
#         self.posns["symbol"].append(contract.localSymbol)
#         self.posns["avgCost"].append(avgCost)
#         self.posns["posn"].append(position)
#         # self.posns["value"].append(value)
#
#     def positionEnd(self):
#         self.df = pd.DataFrame.from_dict(self.posns)  # will make an automatic int index
#
#         if (self.df.empty):
#             self.disconnect()
#             return
#
#         # make req for each posn, use index for reqId
#         for index, row in self.df.iterrows():
#             self.reqPnLSingle(index, row.account, "", row.conId)
#             time.sleep(0.1)
#
#     def pnlSingle(self, reqId: int, pos: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float, value: float):
#         row = self.df.iloc[reqId]
#         # all PnL's are maxint for me at night so I calc the right amount
#         # print(row.symbol, "PnL", unrealizedPnL, "calc", value - row.avgCost * row.posn,'  ',value)
#         self.dic_l.append({'Symbol':row.symbol,'conId':row.conId,'value':round(value),'Quantity':row.posn,'price':value/row.posn,'Account':row.account})
#
#         # just run for ~10 secs
#         if (time.time() - self.start > 10):
#
#             self.disconnect()
#
#     def return_df(self):
#         return pd.DataFrame(self.dic_l)
#
#
# def main():
#     app = TestApp()
#     app.connect("127.0.0.1", 7496, 123)
#     app.run()
#     return app.return_df()
#
# if __name__ == "__main__":
#
#     from datetime import datetime
#     t0 = datetime.now()
#
#
#     print(main())
#     print(datetime.now() - t0)
#
from __future__ import (absolute_import, division, print_function, )
#                        unicode_literals)

import collections
import sys
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
if sys.version_info.major == 2:
    import Queue as queue
    import itertools

    map = itertools.imap

else:  # >= 3
    import queue

import ib.opt
import ib.ext.Contract


class IbManager(object):
    def __init__(self, timeout=20, **kwargs):
        self.q = queue.Queue()
        self.timeout = 20

        self.con = ib.opt.ibConnection(**kwargs)
        self.con.registerAll(self.watcher)

        self.msgs = {
            ib.opt.message.error: self.errors,
            ib.opt.message.updatePortfolio: self.acct_update,
            ib.opt.message.accountDownloadEnd: self.acct_update,
        }

        # Skip the registered ones plus noisy ones from acctUpdate
        self.skipmsgs = tuple(self.msgs.keys()) + (
            ib.opt.message.updateAccountValue,
            ib.opt.message.updateAccountTime)

        for msgtype, handler in self.msgs.items():
            self.con.register(handler, msgtype)

        self.con.connect()

    def watcher(self, msg):
        if isinstance(msg, ib.opt.message.error):
            if msg.errorCode > 2000:  # informative message
                print('-' * 10, msg)

        elif not isinstance(msg, self.skipmsgs):
            print('-' * 10, msg)

    def errors(self, msg):
        if msg.id is None:  # something is very wrong in the connection to tws
            self.q.put((True, -1, 'Lost Connection to TWS'))
        elif msg.errorCode < 1000:
            self.q.put((True, msg.errorCode, msg.errorMsg))

    def acct_update(self, msg):
        self.q.put((False, -1, msg))

    def get_account_update(self,acct):
        self.con.reqAccountUpdates(True, acct)

        portfolio = list()
        while True:
            try:
                err, mid, msg = self.q.get(block=True, timeout=self.timeout)
            except queue.Empty:
                err, mid, msg = True, -1, "Timeout receiving information"
                break

            if isinstance(msg, ib.opt.message.accountDownloadEnd):
                break

            if isinstance(msg, ib.opt.message.updatePortfolio):
                c = msg.contract
                ticker = '%s-%s-%s' % (c.m_symbol, c.m_secType, c.m_exchange)
                conId = c.m_conId
                # print(conId)
                entry = collections.OrderedDict(msg.items())

                # Don't do this if contract object needs to be referenced later
                entry['conId'] = int(conId)  # replace object with the ticker

                portfolio.append(entry)

        # return list of contract details, followed by:
        #   last return code (False means no error / True Error)
        #   last error code or None if no error
        #   last error message or None if no error
        # last error message

        return portfolio, err, mid, msg


def main(acct):
    ibm = IbManager(clientId=5001)

    portfolio, err, errid, errmsg = ibm.get_account_update(acct)



    portfolio = pd.DataFrame(portfolio)
    # portfolio = portfolio.drop(['contract'])
    portfolio = portfolio[['marketValue', 'marketPrice', 'conId']]
    portfolio = portfolio.rename(
        columns={"marketValue": "value", "marketPrice": "price" })
    # print(portfolio)
    return portfolio

if __name__ == "__main__":

    from datetime import datetime
    t0 = datetime.now()


    print(main('U2530531'))
    print(datetime.now() - t0)