import bittrex_api
import json
import pandas
import global_var

API = bittrex_api
BALANCES_FILE = 'balances.json'
UNCOMPLETED_TRADES = 'uncompleted_trades.json'
OVERSOLD_DIVERGENCE = -20
OVERBOUGHT_DIVERGENCE = 20

in_position = False
quantity = 0.005
last_close = 0
last_buy_rate = 0
base_currency = 'BTC'
quote_currency = 'USD'
base_currency_balance = 0
quote_currency_balance = 0
uncompleted_trades = {}


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
    # base_currency_balance = bittrex_api.get_balances(currency=base_currency)
    # quote_currency_balance = bittrex_api.get_balances(currency=quote_currency_balance)

    # test version
    file = open(BALANCES_FILE, 'r')
    data = json.load(file)
    file.close()
    base_currency_balance = data[base_currency]
    quote_currency_balance = data[quote_currency]

    quantity = round(quote_currency_balance / float(API.get_last_candle(global_var.market)['close']) * 0.2, 8)


def load_trades():
    global uncompleted_trades
    file = open(UNCOMPLETED_TRADES, 'r')
    data = json.load(file)
    file.close()
    uncompleted_trades[global_var.market] = data[global_var.market]


def save_balances():
    file = open(BALANCES_FILE, 'w')
    json.dump({base_currency: base_currency_balance, quote_currency: quote_currency_balance}, file,
              ensure_ascii=False, indent=2)
    file.close()


def save_trades():
    file = open(UNCOMPLETED_TRADES, 'w')
    json.dump(uncompleted_trades, file, ensure_ascii=False, indent=2)
    file.close()


def print_balances():
    print(f'CURRENT {quote_currency}_BALANCE: {quote_currency_balance}')
    print(f'CURRENT {base_currency}_BALANCE: {base_currency_balance}')


def buy():
    global last_buy_rate
    try:
        bittrex_api.create_order(global_var.market, bittrex_api.ORDER_DIRECTIONS[0], quantity)
        last_buy_rate = last_close
    except Exception as err:
        print(f'Some error with order occurred: {err}')
        return False
    print('Buy order placed successfully')
    return True


def buy_test():
    global base_currency_balance, quote_currency_balance, last_buy_rate
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
            last_buy_rate = order['rate']
            break
    print_balances()
    save_balances()


def is_sell_profitable(sell_rate, buy_rate):
    fee = float(API.get_trade_fees(global_var.market))
    return (1+fee)/(1-fee) < sell_rate/buy_rate


def sell():
    tmp_quantity = quantity
    for trade in uncompleted_trades[global_var.market]:
        if is_sell_profitable(last_close, trade['rate']):
            tmp_quantity += trade['quantity']
    if tmp_quantity == 0:
        return False
    try:
        bittrex_api.create_order(global_var.market, bittrex_api.ORDER_DIRECTIONS[1], tmp_quantity)
    except Exception as err:
        print(f'Some error with order occurred: {err}')
        return False
    print('Sell order placed successfully')
    return True


def sell_test():
    sell_completed = False
    global base_currency_balance, quote_currency_balance
    fee = float(API.get_trade_fees(market=global_var.market)['takerRate'])
    buy_orders = API.get_orderbook(global_var.market)['bid']
    tmp_quantity = quantity
    for order in buy_orders:
        if float(order['rate']) >= last_close:
            for trade in uncompleted_trades[global_var.market]:
                if is_sell_profitable(order['rate'], trade['rate']):
                    tmp_quantity += trade['quantity']
            if tmp_quantity == 0:
                break
            income = tmp_quantity * float(order['rate'])
            income = income * (1 - fee)
            base_currency_balance -= tmp_quantity
            quote_currency_balance = quote_currency_balance + income
            print(f"SELL RATE: {order['rate']}")
            print(f"INCOME: {income} $")
            print(f"{fee}")
            sell_completed = True
            break
    if sell_completed:
        print_balances()
        save_balances()


def analyse_market(closes):
    global in_position, last_close, quantity
    last_close = closes[global_var.market][len(closes[global_var.market]) - 1]
    if len(closes[global_var.market]) > global_var.rsi_period:
        closes_df = pandas.DataFrame(data={'close': closes[global_var.market]})
        rsi = calculate_rsi(closes_df, global_var.rsi_period)
        macd = calculate_macd(closes_df)
        last_rsi = rsi[len(rsi) - 1]
        last_macd = macd[len(macd) - 1]
        print(f'CURRENT RSI IS {last_rsi}')
        if last_rsi > global_var.rsi_overbought:
            if in_position:
                if is_sell_profitable(last_close, last_buy_rate):
                    print('SELL')
                    sell_test()
                else:
                    uncompleted_trades[global_var.market].append({'quantity': quantity, 'rate': last_buy_rate})
                    print(f'Sell is not profitable. Saving {global_var.market.split("-")[0]} for future tradings')
                    save_trades()
                in_position = False
            elif len(uncompleted_trades[global_var.market]) > 0:
                tmp_quantity = quantity
                quantity = 0
                print('SELL')
                sell_test()
                save_trades()
                quantity = tmp_quantity
            else:
                print("We don't own any, we can't sell")
        if last_rsi < global_var.rsi_oversold:
            if in_position:
                print("We already own it, we won't buy")
            else:
                print('BUY')
                buy_test()
                in_position = True
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
    load_trades()


if __name__ == '__main__':
    load_balances()
    print(quantity)
    closes_t = [47800.140, 47820.140, 47860.140, 47900.140, 47820.140, 47814.140, 47810.140, 47890.140, 47830.120,
                47820.140, 47803.140, 47851.240, 47830.140, 47900.250, 47890.140]
    print(calculate_macd(pandas.DataFrame(data={'close': closes_t})))
