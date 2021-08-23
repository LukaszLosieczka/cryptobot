import bittrex_api
import json
import bittrex_websocket
# import threading
import pandas
from urllib.request import urlopen
from urllib.error import URLError
import time

RSI_PERIOD = 14
RSI_OVERBOUGHT = 75
RSI_OVERSOLD = 25

QUANTITY = 0.005

BALANCES_FILE = 'balances.json'

market = 'BTC-USD'
in_position = False

usd_balance = 1000
btc_balance = 0

balances_history = {'USD': [], 'BTC': []}


def calculate_rsi(closes_df, period, ema=True):
    close_delta = closes_df['close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    if ema:
        # Use exponential moving average
        ma_up = up.ewm(com=period - 1, adjust=True, min_periods=period).mean()
        ma_down = down.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    else:
        # Use simple moving average
        ma_up = up.rolling(window=period, adjust=False).mean()
        ma_down = down.rolling(window=period, adjust=False).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi


def print_balances():
    print(f'CURRENT USD_BALANCE: {usd_balance} $')
    balances_history['USD'].append(usd_balance)
    print(f'CURRENT BTC_BALANCE: {btc_balance} BTC')
    balances_history['BTC'].append(btc_balance)


def buy():
    global usd_balance, btc_balance
    fee = float(bittrex_api.get_trade_fees(market=market)['takerRate'])
    sell_orders = bittrex_api.get_order_book(market)['ask']
    for order in sell_orders:
        cost = float(order['rate']) * QUANTITY
        cost = cost * (1 + fee)
        if cost <= usd_balance:
            usd_balance = usd_balance - cost
            btc_balance = btc_balance + QUANTITY
            print(f"BUY RATE: {order['rate']}")
            print(f"COST: {cost} $")
            print(f"{fee}")
            break
    print_balances()
    save_balances()


def sell():
    global usd_balance, btc_balance
    fee = float(bittrex_api.get_trade_fees(market=market)['takerRate'])
    buy_orders = bittrex_api.get_order_book(market)['bid']
    for order in buy_orders:
        if float(order['quantity']) >= btc_balance:
            income = btc_balance * float(order['rate'])
            income = income * (1 - fee)
            btc_balance = 0
            usd_balance = usd_balance + income
            print(f"SELL RATE: {order['rate']}")
            print(f"INCOME: {income} $")
            print(f"{fee}")
            break
    print_balances()
    save_balances()


def analyse_markets():
    global in_position
    # while True:
    if len(bittrex_websocket.closes['BTC-USD']) > RSI_PERIOD and bittrex_websocket.closes_changed:
        closes_df = pandas.DataFrame(data={'close': bittrex_websocket.closes['BTC-USD']})
        rsi = calculate_rsi(closes_df, RSI_PERIOD)
        # print(rsi)
        last_rsi = rsi[len(rsi) - 1]
        print(f'CURRENT RSI IS {last_rsi}')
        if last_rsi > RSI_OVERBOUGHT:
            if in_position:
                print('SELL')
                sell()
                in_position = False
            else:
                print("We don't own any, we can't sell")
        if last_rsi < RSI_OVERSOLD:
            if in_position:
                print("We already own it, we won't buy")
            else:
                print('BUY')
                buy()
                in_position = True
        bittrex_websocket.closes_changed = False


def save_balances():
    file = open(BALANCES_FILE, 'w')
    json.dump(balances_history, file, ensure_ascii=False, indent=2)


def internet_on():
    try:
        urlopen('https://google.com', timeout=10)
        # print('success')
        time.sleep(60)
        internet_on()
    except URLError as err:
        raise Exception('lost internet connection')


def start_bot():
    bittrex_websocket.add_new_channel(market)
    bittrex_websocket.run()

    # t1 = threading.Thread(target=bittrex_websocket.run)
    # t2 = threading.Thread(target=internet_on)

    # try:
    # t1.start()
    # t2.start()
    # except Exception as err:
    # print('Unexpected error occurred. Rerunning bot...')
    # t1.start()
    # t2.start()


if __name__ == '__main__':
    start_bot()
