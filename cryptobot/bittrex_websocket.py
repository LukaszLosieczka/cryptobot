#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Last tested 2020/09/24 on Python 3.8.5
#
# Note: This file is intended solely for testing purposes and may only be used 
#   as an example to debug and compare with your code. The 3rd party libraries 
#   used in this example may not be suitable for your production use cases.
#   You should always independently verify the security and suitability of any 
#   3rd party library used in your code.

from signalr_aio import Connection  # https://github.com/slazarov/python-signalr-client
from base64 import b64decode
from zlib import decompress, MAX_WBITS
import hashlib
import hmac
import json
import asyncio
import time
import uuid
import bittrex_api
import bot

CANDLE_INTERVAL = ['MINUTE_1', 'MINUTE_5', 'HOUR_1', 'DAY_1']


URL = 'https://socket-v3.bittrex.com/signalr'
API_KEY = bittrex_api.API_KEY
API_SECRET = bittrex_api.API_SECRET
HUB = None
LOCK = asyncio.Lock()
INVOCATION_EVENT = None
INVOCATION_RESPONSE = None


channels = []
closes = {'EMPTY': []}
closes_changed = False
current_candle = None


def add_new_channel(market):
    channel = f'candle_{market}_{CANDLE_INTERVAL[0]}'
    if channel not in channels:
        channels.append(channel)
        closes[market] = []


async def main():
    await connect()
    if API_SECRET != '':
        await authenticate()
    else:
        print('Authentication skipped because API key was not provided')
    await subscribe()
    forever = asyncio.Event()
    await forever.wait()


async def connect():
    global HUB
    connection = Connection(URL)
    HUB = connection.register_hub('c3')
    connection.received += on_message
    connection.error += on_error
    connection.start()
    print('Connected')


async def authenticate():
    timestamp = str(int(time.time()) * 1000)
    random_content = str(uuid.uuid4())
    content = timestamp + random_content
    signed_content = hmac.new(API_SECRET.encode(), content.encode(), hashlib.sha512).hexdigest()

    response = await invoke('Authenticate',
                            API_KEY,
                            timestamp,
                            random_content,
                            signed_content)

    if response['Success']:
        print('Authenticated')
        HUB.client.on('authenticationExpiring', on_auth_expiring)
    else:
        print('Authentication failed: ' + response['ErrorCode'])


async def subscribe():
    HUB.client.on('ticker', on_ticker)
    HUB.client.on('candle', on_candle)
    HUB.client.on('balance', on_balance)

    response = await invoke('Subscribe', channels)
    for i in range(len(channels)):
        if response[i]['Success']:
            print('Subscription to "' + channels[i] + '" successful')
        else:
            print('Subscription to "' + channels[i] + '" failed: ' + response[i]['ErrorCode'])


async def invoke(method, *args):
    async with LOCK:
        global INVOCATION_EVENT
        INVOCATION_EVENT = asyncio.Event()
        HUB.server.invoke(method, *args)
        await INVOCATION_EVENT.wait()
        return INVOCATION_RESPONSE


async def on_message(**msg):
    global INVOCATION_RESPONSE
    if 'R' in msg:
        INVOCATION_RESPONSE = msg['R']
        INVOCATION_EVENT.set()


async def on_error(msg):
    print('Some error occurred...')
    print(msg)


async def on_heartbeat(msg):
    print('\u2661')


async def on_auth_expiring(msg):
    print('Authentication expiring...')
    asyncio.create_task(authenticate())


async def on_ticker(msg):
    await print_message('Ticker', msg)


async def on_candle(msg):
    await analyse_candle(msg)


async def analyse_candle(msg):
    global current_candle, closes_changed
    candle = await process_message(msg[0])
    if current_candle is None:
        current_candle = candle
    if current_candle['delta']['startsAt'] != candle['delta']['startsAt']:
        closes[candle['marketSymbol']].append(float(current_candle['delta']['close']))
        closes_changed = True
        bot.analyse_markets()
        print(f"CLOSED: {current_candle['delta']['startsAt']} {current_candle['delta']['close']}")
    current_candle = candle
    # print(candle)


async def on_balance(msg):
    await print_message('Balance', msg)


async def print_message(title, msg):
    decoded_msg = await process_message(msg[0])
    print(title + ': ' + json.dumps(decoded_msg, indent=2))


async def process_message(message):
    try:
        decompressed_msg = decompress(b64decode(message, validate=True), -MAX_WBITS)
    except SyntaxError:
        decompressed_msg = decompress(b64decode(message, validate=True))
    return json.loads(decompressed_msg.decode())


def run():
    asyncio.run(main())


if __name__ == "__main__":
    add_new_channel('BTC-USD')
    run()
