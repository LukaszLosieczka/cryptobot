import bittrex_api
import json
import pandas
import global_var

API = bittrex_api
QUANTITY = 0.005
BALANCES_FILE = 'balances.json'

in_position = False
base_currency = ''
quote_currency = ''
base_currency_balance = 0
quote_currency_balance = 0


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


def load_balances():
    global base_currency_balance, quote_currency_balance
    # final version
    # base_currency_balance = bittrex_api.get_balances(currency=base_currency)
    # quote_currency_balance = bittrex_api.get_balances(currency=quote_currency_balance)

    # test version
    file = open(BALANCES_FILE, 'r')
    data = json.load(file)
    file.close()
    base_currency_balance = data[base_currency]
    quote_currency_balance = data[quote_currency]


def save_balances():
    file = open(BALANCES_FILE, 'w')
    json.dump({base_currency: base_currency_balance, quote_currency: quote_currency_balance}, file,
              ensure_ascii=False, indent=2)
    file.close()


def print_balances():
    print(f'CURRENT {quote_currency}_BALANCE: {quote_currency_balance}')
    print(f'CURRENT {base_currency}_BALANCE: {base_currency_balance}')


def buy():
    global base_currency_balance, quote_currency_balance
    fee = float(API.get_trade_fees(market=global_var.market)['takerRate'])
    sell_orders = API.get_orderbook(global_var.market)['ask']
    for order in sell_orders:
        cost = float(order['rate']) * QUANTITY
        cost = cost * (1 + fee)
        if cost <= quote_currency_balance:
            quote_currency_balance = quote_currency_balance - cost
            base_currency_balance = base_currency_balance + QUANTITY
            print(f"BUY RATE: {order['rate']}")
            print(f"COST: {cost} $")
            print(f"{fee}")
            break
    print_balances()
    save_balances()


def sell():
    global base_currency_balance, quote_currency_balance
    fee = float(API.get_trade_fees(market=global_var.market)['takerRate'])
    buy_orders = API.get_orderbook(global_var.market)['bid']
    for order in buy_orders:
        if float(order['quantity']) >= base_currency_balance:
            income = base_currency_balance * float(order['rate'])
            income = income * (1 - fee)
            base_currency_balance = 0
            quote_currency_balance = quote_currency_balance + income
            print(f"SELL RATE: {order['rate']}")
            print(f"INCOME: {income} $")
            print(f"{fee}")
            break
    print_balances()
    save_balances()


def analyse_market(closes):
    global in_position
    if len(closes[global_var.market]) > global_var.rsi_period:
        closes_df = pandas.DataFrame(data={'close': closes[global_var.market]})
        rsi = calculate_rsi(closes_df, global_var.rsi_period)
        # print(rsi)
        last_rsi = rsi[len(rsi) - 1]
        print(f'CURRENT RSI IS {last_rsi}')
        if last_rsi > global_var.rsi_overbought:
            if in_position:
                print('SELL')
                sell()
                in_position = False
            else:
                print("We don't own any, we can't sell")
        if last_rsi < global_var.rsi_oversold:
            if in_position:
                print("We already own it, we won't buy")
            else:
                print('BUY')
                buy()
                in_position = True



def check_market(market_symbol):
    markets = API.get_markets()
    for m in markets:
        if m['symbol'] == market_symbol:
            return True
    return False


def start_bot():
    global base_currency, quote_currency
    print('------------------ Bittrex Crypto-Bot ------------------\n')
    while True:
        global_var.market = input('Please enter market symbol to trade in (e.g. BTC-USD): ')
        if not check_market(global_var.market):
            print('Incorrect market symbol')
            continue
        else:
            currencies = global_var.market.split('-')
            base_currency = currencies[0]
            quote_currency = currencies[1]
            break
    while True:
        try:
            global_var.rsi_period = int(input('Please enter RSI period (e.g. 14): '))
        except ValueError:
            continue
        if global_var.rsi_period < 0:
            print('Incorrect RSI period')
            continue
        else:
            break
    while True:
        try:
            global_var.rsi_overbought = int(input('Please enter RSI overbought value (e.g. 70): '))
        except ValueError:
            continue
        if global_var.rsi_overbought < 0 or global_var.rsi_overbought > 100:
            print('Incorrect RSI overbought value')
            continue
        else:
            break
    while True:
        try:
            global_var.rsi_oversold = int(input('Please enter RSI oversold value (e.g. 30): '))
        except ValueError:
            continue
        if global_var.rsi_oversold < 0 or global_var.rsi_oversold > 100:
            print('Incorrect RSI oversold value')
            continue
        else:
            break

    load_balances()


if __name__ == '__main__':
    start_bot()
