from scipy import stats
import requests, json
# from config import *
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib import *
from matplotlib.patches import Rectangle
import pandas

yahoo_header = {'Connection': 'keep-alive',
                'Expires': '-1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
           AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                }


class LongShortEquity:
    def __init__(self, period1, period2):
        # modified later to get request!
        self.companies = instrumentIds = ['ABT', 'AMGN', 'AMD', 'AXP', 'BK', 'BSX',
                                          'CMCSA', 'CVS', 'DIS', 'EA', 'EOG', 'GOOGL', 'GLW', 'HAL',
                                          'HD', 'LOW', 'KO', 'LLY', 'MCD', 'MET', 'NEM',
                                          'PEP', 'PG', 'M', 'SWN', 'T', 'TGT',
                                          'TSLA', 'TXN', 'USB', 'VZ', 'WFC']
        # self.companies = ['TSLA', 'NEM', 'DIS']
        self.closes = []

    def getHistoricalData(self, symbol):
        # historyEndpoint = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?metrics=high&interval=1d&range=3d"
        historyEndpoint = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?metrics=high?&interval=1d&period1={period1}&period2={period2}"
        response = requests.get(historyEndpoint, headers=yahoo_header).json()["chart"]["result"][0]
        times = response["timestamp"]  # is array
        response = response["indicators"]["quote"][0]
        response["times"] = [datetime.datetime.fromtimestamp(i) for i in times]
        self.closes = response["close"]
        res = {
            # "times": response["times"],
            "close": response["close"],
        }
        # res["momentum"] = self.getMomentumNormal(res, period=3)
        res["returns"] = self.getForwardReturns(res, period=1, symbol=symbol)
        return res

    # return an array of future returns (same dimensions as momentum)
    # calculate daily returns!!
    def getForwardReturns(self, history, period, symbol):
        df = history["close"]
        returns = (df[-1]-df[-1-period])/df[-1-period]
        print(f"{self.companies.index(symbol)}/{len(self.companies)} ({symbol}): Past: {df[-1-period]}    Today: {df[-1]}    Returns: {returns}")
        return returns # (present-past)/present

    # def getRankVals(self, history): # takes in history's momentum and return vectors and produces ranking for company
    #     rank, p = stats.spearmanr(history["momentum"], history["returns"])
    #     return rank


period1 = 1669086163 # 11/21/2022
unixDay = 86400
period2 = period1 + 5*unixDay
totalReturns = 0
rets = []
for i in range(20):
    LSE1 = LongShortEquity(period1, period2)
    # update days
    period1 += unixDay
    period2 += unixDay
    df = {}
    for company in LSE1.companies:
        dailyReturn = LSE1.getHistoricalData(company) # the company's returns within a time interval
        df[company] = (dailyReturn["returns"], dailyReturn["close"][-1]) # two values: today's returns (relative to yesterday) and today's value

    df = {k: v for k, v in sorted(df.items(), key=lambda item: item[1][0])}
    rankCount = 1
    dailyReturns = 0
    print("\n")
    positions = 5
    compCount = len(LSE1.companies)
    moneyPerShare = 20000/(2*positions)
    for company, Return_CurrVal in df.items():
        if rankCount <= positions: # if performing well, we sell!
            dailyReturns += (moneyPerShare//Return_CurrVal[-1])*Return_CurrVal[-1]
            print(f"Rank {rankCount}: Shorting {moneyPerShare//Return_CurrVal[-1]} shares ({(moneyPerShare//Return_CurrVal[-1])*Return_CurrVal[-1]}) of {company} @ $+{Return_CurrVal[-1]} with {Return_CurrVal[0]*100}% return")
        elif compCount-positions < rankCount <= compCount:
            dailyReturns -= (moneyPerShare//Return_CurrVal[-1])*Return_CurrVal[-1]
            print(f"Rank {rankCount}: Longing {moneyPerShare//Return_CurrVal[-1]} shares ({(moneyPerShare//Return_CurrVal[-1])*Return_CurrVal[-1]}) of {company} @ $-{Return_CurrVal[-1]} with {Return_CurrVal[0] * 100}% return")
        rankCount += 1
    totalReturns += dailyReturns
    rets.append(dailyReturns)
    print(f"\nDay {i} finished! Daily Returns: {dailyReturns} Cumulative Returns: {totalReturns}\n")

plt.plot(list(range(len(rets))), rets)
plt.show()