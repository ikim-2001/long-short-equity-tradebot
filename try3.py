from concurrent.futures import ThreadPoolExecutor
import requests
import time
from datetime import datetime
from matplotlib import pyplot as plt

start = time.time()
window = 30

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
cum = []

def getData(stock, start, end): # start and end are indices (start and end dates) of close array

    # buy if moving volume is less than current volume and moving close is greater than current cost!!

    # the smaller the rank factor, the better the rank!!

    historyEndpoint = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}?metrics=high&interval=1d&range=366d"
    response = requests.get(historyEndpoint, headers=yahoo_header).json()["chart"]["result"][0]["indicators"]["quote"][0]

    currVol = response["volume"][end]
    currClose = response["close"][end]

    avgVol = sum(response["volume"][start:end])/window
    avgClose = sum(response["close"][start:end])/window

    factorScore = 0

    # BUY CONDITIONS: low avgVol, high currVol & high avgPrice, low currPrice
    # score: rankFactor = CurrVol/AvgVol + AvgClose/CurrClose
    if avgVol <= currVol and avgClose >= currClose:
        factorScore = currVol / avgVol + avgClose / currClose

    # SELL CONDITIONS: high avgVol, low currVol & low avgPrice, high currPrice
    # score: rankFactor = - AvgVol/currVal - currClose / avgClose
    elif avgVol > currVol and avgClose < currClose:
        factorScore -= ((avgVol / currClose) + (currClose / avgClose))

    return [stock, factorScore, currClose]
    # another idea is to have zero if both conditions not met, else,, do as above

# create a thread pool
executor = ThreadPoolExecutor(30)
# map()
for i in list(range(window, 365)):

    # print(f"\n{datetime.fromtimestamp(period1)} to {datetime.fromtimestamp(period2)}: Day {i}")
    print(i)
    df = {} # this is the total
    startArr = [i-window]*compCount
    endArr = [i]*compCount
    for stock, factorScore, currClose in executor.map(getData, stocks, startArr, endArr):
        df[stock]=[factorScore, currClose]
    fullReport = {k: v for k, v in sorted(df.items(), key=lambda item: item[1][0])}

    rankCount = 1
    dailyReturns = 0
    positions = 5
    OGBudget = 20000
    moneyPerShare = OGBudget / (2 * positions)
    for company, Return_CurrVal in fullReport.items():
        if rankCount <= positions:  # if performing well, we sell!
            dailyReturns += (moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]
            print(
                f"Rank {rankCount}: Shorting {moneyPerShare // Return_CurrVal[-1]} shares ({(moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]}) of {company} @ $+{Return_CurrVal[-1]} with {Return_CurrVal[0]} score")
        elif compCount - positions < rankCount <= compCount:
            dailyReturns -= (moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]
            print(
                f"Rank {rankCount}: Longing {moneyPerShare // Return_CurrVal[-1]} shares ({(moneyPerShare // Return_CurrVal[-1]) * Return_CurrVal[-1]}) of {company} @ $-{Return_CurrVal[-1]} with {Return_CurrVal[0]} score")
        rankCount += 1
    totalReturns += dailyReturns
    rets.append(totalReturns)
    print(f"\nDay {i} finished! Daily Returns: {dailyReturns} Cumulative Returns: {totalReturns}")
    currBudget = OGBudget+totalReturns
    cumDelta= ((currBudget-OGBudget)/OGBudget)*100
    cum.append(currBudget)
    print(f"You now have ${currBudget}, which is {cumDelta}% of ${OGBudget}")


    end = time.time()
    print(end - start)
    start = time.time()


plt.plot(list(range(len(rets))), rets)
plt.show()