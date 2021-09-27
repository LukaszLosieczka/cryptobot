import time
import bittrex_api
import json
import pandas
import global_var

API = bittrex_api
BALANCES_FILE = 'balances.json'
DATA_FILE = 'data_file.json'
OVERSOLD_DIVERGENCE = -20
OVERBOUGHT_DIVERGENCE = 20
MINIMUM_TRADE_SIZE = 0.0001

in_position = False
quantity = 0.005
last_close = 0
last_buy_rate = 0
base_currency = 'BTC'
quote_currency = 'USD'
base_currency_balance = 0
quote_currency_balance = 0
uncompleted_trades = {}
transactions = {}


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
        ma_up = up.rolling(window=period).mean()
        ma_down = down.rolling(window=period).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi


def calculate_macd(closes_df, fast_length=12, slow_length=26, length=9):
    k = closes_df['close'].ewm(span=fast_length, adjust=False, min_periods=fast_length).mean()
    d = closes_df['close'].ewm(span=slow_length, adjust=False, min_periods=slow_length).mean()
    macd = k - d
    macd_s = macd.ewm(span=length, adjust=False, min_periods=length).mean()
    macd_h = macd - macd_s
    return macd_h


def load_balances():
    global base_currency_balance, quote_currency_balance, quantity
    # final version
    base_currency_balance = float(bittrex_api.get_balances(currency=base_currency)['total'])
    quote_currency_balance = float(bittrex_api.get_balances(currency=quote_currency)['total'])
    quantity = round(quote_currency_balance / float(API.get_last_candle(global_var.market)['close']) * 0.2, 8)

    # test version
    # file = open(BALANCES_FILE, 'r')
    # data = json.load(file)
    # file.close()
    # base_currency_balance = data[base_currency]
    # quote_currency_balance = data[quote_currency]


def save_balances():
    file = open(BALANCES_FILE, 'w')
    json.dump({base_currency: base_currency_balance, quote_currency: quote_currency_balance}, file,
              ensure_ascii=False, indent=2)
    file.close()


def load_data():
    global transactions, uncompleted_trades, in_position, quantity, last_buy_rate
    try:
        file = open(DATA_FILE, 'r')
        data = json.load(file)
        file.close()
        transactions[global_var.market] = data['transactions'][global_var.market]
        uncompleted_trades[global_var.market] = data['uncompleted_trades'][global_var.market]
        in_position = data['in_position']
        quantity = data['quantity']
        last_buy_rate = data['last_buy_rate']
    except IOError and KeyError:
        print('Data file is corrupted')
        transactions[global_var.market] = []
        uncompleted_trades[global_var.market] = []


def save_data():
    try:
        file = open(DATA_FILE, 'w')
        data = {'balances': {quote_currency: quote_currency_balance, base_currency: base_currency_balance},
                'transactions': transactions,
                'uncompleted_trades': uncompleted_trades,
                'in_position': in_position,
                'quantity': quantity,
                'last_buy_rate': last_buy_rate}
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.close()
    except IOError:
        print('Data file is corrupted')


def print_balances():
    print(f'CURRENT {quote_currency}_BALANCE: {quote_currency_balance}')
    print(f'CURRENT {base_currency}_BALANCE: {base_currency_balance}')


def buy():
    global last_buy_rate, quantity
    load_balances()
    if quantity < MINIMUM_TRADE_SIZE:
        print('We don t have enough resource to buy')
        return False
    try:
        response = API.create_order(global_var.market, API.ORDER_DIRECTIONS[0], quantity)
        last_buy_rate = last_close
    except Exception as err:
        print(f'Some error with order occurred: {err}')
        return False
    if not response:
        print(f'Some error with order occurred: {response}')
        return False
    print(f'Buy order placed successfully:\n{response}')
    transaction = {'direction': 'BUY',
                   'rate': last_close,
                   'quantity': quantity,
                   'time': time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime())}
    transactions[global_var.market].append(transaction)
    return True


def buy_test():
    global base_currency_balance, quote_currency_balance, last_buy_rate, quantity
    quantity = round(quote_currency_balance / float(API.get_last_candle(global_var.market)['close']) * 0.2, 8)
    if quantity == 0:
        print('We don t have enough resource to buy')
        return False
    fee = float(API.get_trade_fees(market=global_var.market)['takerRate'])
    sell_orders = API.get_orderbook(global_var.market)['ask']
    for order in sell_orders:
        cost = float(order['rate']) * quantity
        cost = cost * (1 + fee)
        if cost <= quote_currency_balance:
            quote_currency_balance = quote_currency_balance - cost
            base_currency_balance = base_currency_balance + quantity
            print(f"BUY RATE: {order['rate']}")
            print(f"COST: {cost} $")
            print(f"{fee}")
            last_buy_rate = float(order['rate'])
            transaction = {'direction': 'BUY',
                           'rate': float(order["rate"]),
                           'quantity': quantity,
                           'time': time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime())}
            transactions[global_var.market].append(transaction)
            break
    print_balances()
    save_balances()


def is_sell_profitable(sell_rate, buy_rate):
    fee = float(API.get_trade_fees(market=global_var.market)['takerRate'])
    return (1+fee)/(1-fee) < sell_rate/buy_rate


def sell():
    tmp_quantity = quantity
    new_trades = []
    for trade in uncompleted_trades[global_var.market]:
        if is_sell_profitable(last_close, trade['rate']):
            tmp_quantity += trade['quantity']
        else:
            new_trades.append(trade)
    if tmp_quantity == 0:
        print('Can t sell uncompleted trades')
        return False
    uncompleted_trades[global_var.market] = new_trades
    try:
        response = API.create_order(global_var.market, API.ORDER_DIRECTIONS[1], tmp_quantity)
    except Exception as err:
        print(f'Some error with order occurred: {err}')
        return False
    if not response:
        print(f'Some error with order occurred: {response}')
        return False
    print(f'Sell order placed successfully:\n{response}')
    transaction = {'direction': 'SELL',
                   'rate': last_close,
                   'quantity': tmp_quantity,
                   'time': time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime())}
    transactions[global_var.market].append(transaction)
    return True


def sell_test():
    global base_currency_balance, quote_currency_balance
    fee = float(API.get_trade_fees(market=global_var.market)['takerRate'])
    order = API.get_orderbook(global_var.market)['bid'][0]
    tmp_quantity = quantity
    new_trades = []
    for trade in uncompleted_trades[global_var.market]:
        if is_sell_profitable(float(order['rate']), trade['rate']):
            tmp_quantity += trade['quantity']
        else:
            new_trades.append(trade)
    if tmp_quantity == 0:
        print('sell was not successful')
        return False
    uncompleted_trades[global_var.market] = new_trades
    income = tmp_quantity * float(order['rate'])
    income = income * (1 - fee)
    base_currency_balance -= tmp_quantity
    quote_currency_balance = quote_currency_balance + income
    print(f"SELL RATE: {order['rate']}")
    print(f"INCOME: {income} $")
    print(f"{fee}")
    transaction = {'direction': 'SELL',
                   'rate': float(order["rate"]),
                   'quantity': tmp_quantity,
                   'time': time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime())}
    transactions[global_var.market].append(transaction)
    print_balances()
    save_balances()


def analyse_market(closes):
    global in_position, last_close, quantity
    last_close = closes[global_var.market][len(closes[global_var.market]) - 1]
    if len(closes[global_var.market]) > global_var.rsi_period:
        closes_df = pandas.DataFrame(data={'close': closes[global_var.market]})
        rsi = calculate_rsi(closes_df, global_var.rsi_period)
        # macd = calculate_macd(closes_df)
        last_rsi = rsi[len(rsi) - 1]
        # last_macd = macd[len(macd) - 1]
        print(f'CURRENT RSI IS {last_rsi}')
        if last_rsi > global_var.rsi_overbought:
            if in_position:
                if is_sell_profitable(last_close, last_buy_rate):
                    print('SELL')
                    sell()
                else:
                    uncompleted_trades[global_var.market].append({'quantity': quantity, 'rate': last_buy_rate})
                    print(f'Sell is not profitable. Saving {global_var.market.split("-")[0]} for future tradings')
                in_position = False
            if len(uncompleted_trades[global_var.market]) > 0:
                tmp_quantity = quantity
                quantity = 0
                print('SELL UNCOMPLETED TRADES')
                sell()
                quantity = tmp_quantity
            else:
                print("We don't own any, we can't sell")
        if last_rsi < global_var.rsi_oversold:
            if in_position:
                if last_rsi < 10 and last_close < last_buy_rate:
                    uncompleted_trades[global_var.market].append({'quantity': quantity, 'rate': last_buy_rate})
                    print(f'Saving last trade to uncompleted trades')
                    print('BUY')
                    buy()
                else:
                    print("We already own it, we won't buy")
            else:
                print('BUY')
                buy()
                in_position = True
        save_data()
        print(f'In position: {in_position}\n')


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
        global_var.market = 'BTC-USD'  # input('Please enter market symbol to trade in (e.g. BTC-USD): ')
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
            global_var.rsi_period = 14  # int(input('Please enter RSI period (e.g. 14): '))
        except ValueError:
            continue
        if global_var.rsi_period < 0:
            print('Incorrect RSI period')
            continue
        else:
            break
    while True:
        try:
            global_var.rsi_overbought = 85  # int(input('Please enter RSI overbought value (e.g. 70): '))
        except ValueError:
            continue
        if global_var.rsi_overbought < 0 or global_var.rsi_overbought > 100:
            print('Incorrect RSI overbought value')
            continue
        else:
            break
    while True:
        try:
            global_var.rsi_oversold = 15  # int(input('Please enter RSI oversold value (e.g. 30): '))
        except ValueError:
            continue
        if global_var.rsi_oversold < 0 or global_var.rsi_oversold > 100:
            print('Incorrect RSI oversold value')
            continue
        else:
            break

    load_balances()
    load_data()


def bot_test():
    closes24h = API.get_candles('BTC-USD')
    closes = []
    start_bot()
    for close in closes24h:
        closes.append(float(close['close']))
        if len(closes) >= 14:
            analyse_market({'BTC-USD': closes})


if __name__ == '__main__':
    global_var.market = 'BTC-USD'
    load_balances()
    print(quote_currency_balance)
    print(base_currency_balance)
    quantity = 0.00010151
    last_close = float(API.get_last_candle(global_var.market)['close'])
    uncompleted_trades['BTC-USD'] = []
    transactions['BTC-USD'] = []
    last_buy_rate = 43332.79992119
    if is_sell_profitable(last_close, last_buy_rate):
        sell()
    else:
        print('Not profitable')
