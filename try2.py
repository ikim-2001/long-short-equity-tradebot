from concurrent.futures import ThreadPoolExecutor
import requests
import time
from datetime import datetime
from matplotlib import pyplot as plt

start = time.time()

yahoo_header = {'Connection': 'keep-alive',
                'Expires': '-1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
           AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                }
stocks = ['ABT', 'AMGN', 'AMD', 'AXP', 'BK', 'BSX',
                                          'CMCSA', 'CVS', 'DIS', 'EA', 'EOG', 'GOOGL', 'GLW', 'HAL',
                                          'HD', 'LOW', 'KO', 'LLY', 'MCD', 'MET', 'NEM',
                                          'PEP', 'PG', 'M', 'SWN', 'T', 'TGT',
                                          'TSLA', 'TXN', 'USB', 'VZ', 'WFC']

# period1 = 1669086163 # 11/21/2022
# unixDay = 86400
# period2 = period1 + 5*unixDay
totalReturns = 0
compCount = len(stocks)
rets = []

def getData(stock, start, end, timeGap=1): # start and end are indices (start and end dates) of close array
    historyEndpoint = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}?metrics=high&interval=1d&range=100d"
    response = requests.get(historyEndpoint, headers=yahoo_header).json()["chart"]["result"][0]["indicators"]["quote"][0]

    df = response["close"]

    # core part of algorithm
    returns = (df[end] - df[start]) / df[start] # (now-past)/past
    print(f"{stocks.index(stock)}/{len(stocks)} ({stock}): Past: {df[start]}    Today: {df[end]}    Returns: {returns}")
    return [stock, returns, df[end]]


# create a thread pool
executor = ThreadPoolExecutor(30)
# map()
for i in list(range(1, 60)):

    # print(f"\n{datetime.fromtimestamp(period1)} to {datetime.fromtimestamp(period2)}: Day {i}")
    print(i)
    df = {} # this is the total
    startArr = [i-1]*compCount
    endArr = [i]*compCount
    for stock, returnRate, stockPrice in executor.map(getData, stocks, startArr, endArr):
        df[stock]=[returnRate, stockPrice]
    fullReport = {k: v for k, v in sorted(df.items(), key=lambda item: item[1][0])}

    rankCount = 1
    dailyReturns = 0
    positions = 5
    moneyPerShare = 20000 / (2 * positions)
    for company, Return_CurrVal in fullReport.items():
        if rankCount <= positions:  # if performing well, we sell!
            dailyReturns += (moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]
            print(
                f"Rank {rankCount}: Shorting {moneyPerShare // Return_CurrVal[-1]} shares ({(moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]}) of {company} @ $+{Return_CurrVal[-1]} with {Return_CurrVal[0] * 100}% return")
        elif compCount - positions < rankCount <= compCount:
            dailyReturns -= (moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]
            print(
                f"Rank {rankCount}: Longing {moneyPerShare // Return_CurrVal[-1]} shares ({(moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]}) of {company} @ $-{Return_CurrVal[-1]} with {Return_CurrVal[0] * 100}% return")
        rankCount += 1
    totalReturns += dailyReturns
    rets.append(totalReturns)
    print(f"\nDay {i} finished! Daily Returns: {dailyReturns} Cumulative Returns: {totalReturns}\n")


    end = time.time()
    print(end - start)
    start = time.time()


plt.plot(list(range(len(rets))), rets)
plt.show()