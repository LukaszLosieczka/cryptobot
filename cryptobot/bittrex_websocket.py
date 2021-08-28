from urllib.request import urlopen
from urllib.error import URLError
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
import global_var

CANDLE_INTERVAL = ['MINUTE_1', 'MINUTE_5', 'HOUR_1', 'DAY_1']


URL = 'https://socket-v3.bittrex.com/signalr'
CONNECTION = Connection(URL)
HUB = CONNECTION.register_hub('c3')
LOCK = asyncio.Lock()
INVOCATION_EVENT = asyncio.Event()
INVOCATION_RESPONSE = {}


channels = []
closes = {'EMPTY': []}
received_messages = []
closes_changed = False
current_candle = None
last_close = None
is_subscribed = False
forever = asyncio.Event()


def add_new_channel(market):
    channel = f'candle_{market}_{CANDLE_INTERVAL[0]}'
    if channel not in channels:
        channels.append(channel)
        closes[market] = []


def internet_on():
    try:
        urlopen('https://google.com', timeout=100)
        return True
    except URLError:
        return False


async def update_lost_candles(min_range):
    global current_candle, closes_changed, last_close
    lost_candles = bittrex_api.get_candles(global_var.market)
    last_index = len(lost_candles) - 1
    for i in range(min_range, 0, -1):
        candle = lost_candles[last_index - i]
        if candle not in received_messages:
            received_messages.append(candle)
            closes[global_var.market].append(float(candle['close']))
            closes_changed = True
            print(f"LOST CANDLE: {get_time()} closed at {candle['delta']['close']}"
                  f"{global_var.market.split('-')[1]}")
            last_close = {'delta': candle}
    current_candle = {'delta': lost_candles[last_index]}


def seconds_to_close():
    current_second = int(time.strftime('%S', time.gmtime()))
    return 60 - current_second + 5


async def check_update():
    lost_minutes = 1
    while True:
        old_close = last_close
        await asyncio.sleep(seconds_to_close())
        # print('checking update')
        if last_close == old_close:
            try:
                await on_close('Lost internet connection')
                await update_lost_candles(lost_minutes)
                lost_minutes = 1
            except OSError:
                lost_minutes += 1


async def start_client():
    await connect()
    if global_var.api_secret != '':
        await authenticate()
    else:
        print('Authentication skipped because API key was not provided')
    await subscribe()
    await check_update()


async def connect():
    CONNECTION.received += on_message
    CONNECTION.error += on_error
    CONNECTION.start()
    print('Connected')


async def authenticate():
    timestamp = str(int(time.time()) * 1000)
    random_content = str(uuid.uuid4())
    content = timestamp + random_content
    signed_content = hmac.new(global_var.api_secret.encode(), content.encode(), hashlib.sha512).hexdigest()

    response = await invoke('Authenticate',
                            global_var.api_key,
                            timestamp,
                            random_content,
                            signed_content)

    if response['Success']:
        print('Authenticated')
        HUB.client.on('authenticationExpiring', on_auth_expiring)
    else:
        print('Authentication failed: ' + response['ErrorCode'])


async def subscribe():
    global is_subscribed
    HUB.client.on('ticker', on_ticker)
    HUB.client.on('candle', on_candle)
    HUB.client.on('balance', on_balance)

    response = await invoke('Subscribe', channels)
    for i in range(len(channels)):
        if response[i]['Success']:
            print('Subscription to "' + channels[i] + '" successful')
        else:
            print('Subscription to "' + channels[i] + '" failed: ' + response[i]['ErrorCode'])
    is_subscribed = True


async def unsubscribe():
    global is_subscribed
    response = await invoke('Unsubscribe', channels)
    for i in range(len(channels)):
        if response[i]['Success']:
            print(channels[i] + ' unsubscribed')
        else:
            print(channels[i] + ' failed to unsubscribe: ' + response[i]['ErrorCode'])
    is_subscribed = False


async def invoke(method, *args):
    async with LOCK:
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


async def on_close(msg):
    global LOCK
    print('Connection is closed. Trying to reconnect...')
    received_messages.append(msg)
    if internet_on():
        LOCK = asyncio.Lock()
        asyncio.create_task(connect())
        asyncio.create_task(authenticate())
        asyncio.create_task(subscribe())
    else:
        print(f'Reconnecting failed. Next attempt in {seconds_to_close()} seconds')
        raise OSError


async def on_heartbeat(msg):
    received_messages.append(msg)
    print('\u2661')


async def on_auth_expiring(msg):
    print('Authentication expiring...')
    received_messages.append(msg)
    asyncio.create_task(authenticate())


async def on_ticker(msg):
    await print_message('Ticker', msg)


async def on_candle(msg):
    await analyse_candle(msg)


def get_time():
    t = float(time.strftime('%H.%M', time.localtime()))
    date = time.strftime('%Y-%m-%d', time.localtime())
    # t = float('22.01')
    t -= 0.01
    t = round(t, 2)
    hours = str(t).split('.')[0]
    minutes = str(t).split('.')[1]
    if minutes == '99':
        minutes = '59'
    if hours == '-0':
        hours = '23'
        minutes = '59'
        date = time.strftime('%Y-%m-%d', time.gmtime())
    if len(hours) == 1:
        hours = f'0{hours}'
    if len(minutes) == 1:
        minutes = f'{minutes}0'
    return f'{date}, {hours}:{minutes}'


async def analyse_candle(msg):
    global current_candle, closes_changed, last_close
    candle = await process_message(msg[0])
    # print(current_candle)
    # print(candle)
    if current_candle['delta']['startsAt'] != candle['delta']['startsAt'] and current_candle not in received_messages:
        received_messages.append(current_candle)
        closes[candle['marketSymbol']].append(float(current_candle['delta']['close']))
        closes_changed = True
        last_close = current_candle
        bot.analyse_market(closes)
        print(f"{get_time()} closed at {current_candle['delta']['close']} "
              f"{global_var.market.split('-')[1]}")
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
    global current_candle
    bot.start_bot()
    add_new_channel(global_var.market)
    current_candle = {'delta': bittrex_api.get_last_candle(global_var.market)}
    asyncio.run(start_client())


async def test1():
    add_new_channel('BTC-USD')
    await connect()
    global_var.api_secret = ''
    global_var.api_key = ''
    await authenticate()
    await subscribe()
    time.sleep(5)
    await unsubscribe()

if __name__ == "__main__":
    asyncio.run(test1())
    print(get_time())
    # print(seconds_to_close())
    # add_new_channel('BTC-USD')
    # run()
