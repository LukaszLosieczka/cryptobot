import time
import hashlib
import hmac
import json
import requests


API_URL = 'https://api.bittrex.com/v3'
API_KEY = 'c06a80c7cccb4f65ac5c0c6f08cbc121'
API_SECRET = '1c335acf0b8c4cddbd899a751d98455c'

ORDER_DIRECTIONS = ['BUY', 'SELL']


def authentication_headers(url, request_method, request_body=None):
    time_stamp = str(int(time.time() * 1000))
    content_hash = hashlib.sha512((json.dumps(request_body) if request_body else '').encode()).hexdigest()
    pre_sign = ''.join((time_stamp, url, request_method, content_hash))
    signature = hmac.new(API_SECRET.encode(), pre_sign.encode(), hashlib.sha512).hexdigest()
    return {
        'Api-Key': API_KEY,
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


def get_order_book(market, depth=25):
    url = f'{API_URL}/markets/{market}/orderbook'
    headers = {'depth': str(depth)}
    return request_get(url, headers=headers)


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
    print(get_balances('BTC'))
