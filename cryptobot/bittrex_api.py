import time
import hashlib
import hmac
import json
import requests
import global_var


API_URL = 'https://api.bittrex.com/v3'
ORDER_DIRECTIONS = ['BUY', 'SELL']


def authentication_headers(url, request_method, request_body=None):
    time_stamp = str(int(time.time() * 1000))
    content_hash = hashlib.sha512((json.dumps(request_body) if request_body else '').encode()).hexdigest()
    pre_sign = ''.join((time_stamp, url, request_method, content_hash))
    signature = hmac.new(global_var.api_secret.encode(), pre_sign.encode(), hashlib.sha512).hexdigest()
    return {
        'Api-Key': global_var.api_key,
        'Api-Timestamp': time_stamp,
        'Api-Content-Hash': content_hash,
        'Api-Signature': signature
    }


def request_get(url, headers=None):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return response.json()['code']
    else:
        return response.json()


def request_post(url, headers, data):
    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 200:
        return response.json()['code']
    else:
        return response.json()


def get_trade_fees(market=''):
    url = f'{API_URL}/account/fees/trading'
    if market != '':
        url += f'/{market}'
    headers = authentication_headers(url, 'GET')
    return request_get(url, headers=headers)


def get_balances(currency=''):
    url = f'{API_URL}/balances'
    if currency != '':
        url += f'/{currency}'
    headers = authentication_headers(url, 'GET')
    return request_get(url, headers=headers)


def get_orderbook(market, depth=25):
    url = f'{API_URL}/markets/{market}/orderbook'
    headers = {'depth': str(depth)}
    return request_get(url, headers=headers)


def get_candles(market, candle_interval='MINUTE_1'):
    url = f'{API_URL}/markets/{market}/candles/{candle_interval}/recent'
    return request_get(url)


def get_last_candle(market, candle_interval='MINUTE_1'):
    last_candles = get_candles(market, candle_interval=candle_interval)
    return last_candles[len(last_candles) - 1]


def get_markets():
    url = f'{API_URL}/markets'
    return request_get(url)


def create_order(market, direction, quantity, use_awards=False):
    order = {
        'marketSymbol': market,
        'direction': direction,
        'type': None,
        'quantity': quantity,
        'ceiling': None,
        'limit': None,
        'timeInForce': None,
        'clientOrderId': None,
        'useAwards': use_awards
    }
    order_json = json.dumps(order)
    url = f'{API_URL}/orders'
    headers = authentication_headers(url, 'POST', request_body=order_json)
    return request_post(url, headers, order_json)


if __name__ == '__main__':
    for i in range(9, 5, -1):
        print(i)
    # print(get_candles('BTC-USD'))
