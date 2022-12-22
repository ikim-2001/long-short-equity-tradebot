import requests, json
from config import *
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib import *
from matplotlib.patches import Rectangle


base_endpoint = "https://paper-api.alpaca.markets"
account_url = f"{base_endpoint}/v2/account"
order_url = f"{base_endpoint}/v2/orders"

# historical_url = f""

yahoo_header = {'Connection': 'keep-alive',
           'Expires': '-1',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
           AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
           }

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
  }



def get_account_info():
  account_info = requests.get(account_url, headers=headers)
  return account_info

def get_orders():
  portfolio_url = f"{base_endpoint}/v2/positions"
  response = requests.get(portfolio_url, headers=headers)
  # for key, value in json.load(response.json()):
  for asset in (response.json()):
    print(asset)

fig, ax = plt.subplots()
def get_14_days(symbol, window): # string -> dict
  history_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?metrics=high&interval=1d&range=150d"
  print(history_url)
  response = requests.get(history_url, headers=yahoo_header).json()["chart"]["result"][0]
  times = response["timestamp"] # is array
  response = response["indicators"]["quote"][0]
  print(len(times), len(response["close"]))
  response["move_avg_close"], response["move_avg_volume"] = [], []
  response["times"] = [datetime.datetime.fromtimestamp(i) for i in times]
  ax.plot(times, response["close"], label=f"{symbol}")
  ax.legend()

  for key, value in response.items():
    for i in range(len(value)):
      if i >= window:
        if key in ["close", "volume"]:
          moving_avg = sum(value[i - window:i]) / window
          # buy when moving average is less than volume
          if key == "close":
            response["move_avg_close"].append((response["times"][i], moving_avg, value[i], moving_avg > value[i]))
          # sell when moving volume is greater than current volume
          if key == "volume":
            response["move_avg_volume"].append((response["times"][i], moving_avg, value[i], moving_avg < value[i]))
  return response

def buy_and_sell(symbol, window):
  df = get_14_days(symbol, window)
  move_avg_close = df["move_avg_close"]
  move_avg_volume = df["move_avg_volume"]
  z = 1
  start_price = df["close"][0]
  end_pice = df["close"][-1]
  print(f"START PRICE {start_price}\n")
  PL = 0
  for i in range(len(move_avg_close)):
    # print(move_avg_volume[i])
    if move_avg_volume[i][-1] and move_avg_close[i][-1]:
      if z == 1:
        close_adj = move_avg_close[i]
        print(close_adj, "-BUY")
        PL -= close_adj[2]
        print(PL)
        z -= 1
        unix_moment = time.mktime(close_adj[0].timetuple())
        ax.add_patch(Rectangle((unix_moment-0.01 * 10 ** 7, close_adj[2]-1.5), 0.02 * 10 ** 7, 3, facecolor='green', edgecolor = 'black', fill=True, lw=1))
    elif not move_avg_volume[i][-1] and not move_avg_close[i][-1]:
      if z == 0:
        close_adj = move_avg_close[i]
        print(close_adj, "-SELL")
        PL += close_adj[2]
        return_per = PL / start_price
        print("Total Profit/Loss $", round(PL, 2))
        print("Total Return %", return_per*100, "\n")
        unix_moment = time.mktime(close_adj[0].timetuple())
        ax.add_patch(Rectangle((unix_moment-0.01 * 10 ** 7, close_adj[2]-1.5), 0.02 * 10 ** 7, 3, facecolor='red', edgecolor = 'black', fill=True, lw=1))
        z += 1
# buy_and_sell("GOOGL", 20)
# buy_and_sell("AAPL", 20)
# buy_and_sell("AMZN", 20)
# plt.show()



def create_order(symbol, qty, side, type, time_in_force):
  data = {
    "symbol": symbol,
    "qty": qty,
    "side": side,
    "type": type,
    "time_in_force": time_in_force
  }

  r = requests.post(order_url, json=data, headers=headers)

  return json.loads(r.content)

response = create_order("GOOGL", 5, "buy", "market", "gtc")
print(response)