# BINANCE TRACKER

# Augustin BRISSART
# GitHub: @augustin999

# June 2021


import numpy as np
import time as tm
import hmac
import json
import hashlib
import requests
from urllib.parse import urlencode

try:
    from tracker import utils
    from tracker import config
except:
    import utils
    import config

def read_keys():
    api_key = utils.read_file(path=config.public_key_path)
    api_secret = utils.read_file(path=config.private_key_path)
    if type(api_key) == bytes:
        api_key = api_key.decode('utf-8')
    if type(api_secret) == bytes:
        api_secret = api_secret.decode('utf-8')
    return api_key, api_secret


KEY, SECRET = read_keys()
BASE_URL_FUTURES = 'https://fapi.binance.com'
BASE_URL_SPOT = 'https://api.binance.com'

# SETTING UP SIGNATURE
# --------------------

def hashing(query_string: str):
    """ Build hashed signature for identification """
    hmac_signature = hmac.new(SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    return hmac_signature.hexdigest()


def dispatch_request(http_method: str):
    """ Prepare a request with given http method """
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json;charset=utf-8',
        'X-MBX-APIKEY': KEY
    })
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post,
    }.get(http_method, 'GET')


def send_signed_request(base_url: str, http_method: str, url_path: str, payload={}):
    """ 
    Prepare and send a signed request.
    Use this function to obtain private user info, manage trades and track accounts.
    """
    query_string = urlencode(payload)
    # Replace single quotes to double quotes
    query_string = query_string.replace('%27', '%22')
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, get_server_time())
    else:
        query_string = 'timestamp={}'.format(get_server_time())
    url = base_url + url_path + '?' + query_string + '&signature=' + hashing(query_string)
    params = {'url': url, 'params': {}}
    response = dispatch_request(http_method)(**params)
    return response.json()


def send_public_request(base_url: str, url_path: str, payload={}):
    """
    Prepare and send an unsigned request.
    Use this function to obtain public market data
    """
    query_string = urlencode(payload, True)
    url = base_url + url_path
    if query_string:
        url = url + '?' + query_string
    response = dispatch_request('GET')(url=url)
    return response.json()


# GENERAL ENDPOINTS
# -----------------

def test_connectivity(market: str):
    """ Check if server is on or not """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/ping' if base_url == BASE_URL_FUTURES else '/api/v3/ping'
    ping = send_public_request(base_url, url_path)
    return ping == {}


def get_server_time(market: str):
    """ Returns current time in milliseconds on the Binance server (it can be different from local time)"""
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/time' if base_url == BASE_URL_FUTURES else '/api/v3/time'
    serverTime = send_public_request(base_url, url_path)['serverTime']
    return serverTime


def get_exchange_info(market: str):
    """ Returns current exchange trading rules and symbols information """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/exchangeInfo' if base_url == BASE_URL_FUTURES else '/api/v3/exchangeInfo'
    exchange_info = send_public_request(base_url, url_path)
    return exchange_info


# MARKET DATA ENDPOINTS
# -----------------

def get_order_book(market: str, pair: str, limit=20):
    """
    Returns bids and asks for the specified pair.

    Arguments:
        pair (str): single pair
        limit (int): Valid limits are [5, 10, 20, 50, 100, 500, 1000]

    Response:
        {
            'lastUpdateId' (int),
            'E' (unix timestamp), 
            'T' (unix timestamp),
            'bids' (list of [price (str), quantity (str)]),
            'asks' (list of [price (str), quantity (str)])
        }
    """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/depth' if base_url == BASE_URL_FUTURES else '/api/v3/depth'
    params = {'symbol': pair.upper(), 'limit': limit}
    order_book = send_public_request(base_url, url_path, params)
    for i in range(limit):
        order_book['bids'][i] = [np.float64(order_book['bids'][i][0]), np.float64(order_book['bids'][i][1])]
        order_book['asks'][i] = [np.float64(order_book['asks'][i][0]), np.float64(order_book['asks'][i][1])]
    return order_book


def get_recent_trades(market: str, pair: str, limit=20):
    """
    Returns the latest trades performed on the Binance Futures market.
    
    Arguments:
        pair (str): single pair
        limit (int): less or equal to 1000
    
    Response:
        list of trades: [
            {
                'id' (int),
                'price' (float),
                'qty' (float),
                'quoteQty' (float),
                'time' (unix timestamp),
                'isBuyerMaker' (bool)
            }
        ]
    """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/trades' if base_url == BASE_URL_FUTURES else '/api/v3/trades'
    params = {'symbol': pair.upper(), 'limit': limit}
    trades = send_public_request(base_url, url_path, params)
    for trade in trades:
        trade['price'] = np.float64(trade['price'])
        trade['qty'] = np.float64(trade['qty'])
        trade['quoteQty'] = np.float64(trade['quoteQty'])
    return trades


def get_old_trades(market: str, pair: str, limit=100, fromId=None):
    """
    Get older market historical trades.

    Arguments:
        pair (str): single pair
        limit (int): less or equal to 1000
        fromId (int): Trade Id to fetch from (optional). Default gets most recent trades.

    Response:
        list of trades: [
            {
                'id' (int),
                'price' (float),
                'qty' (float),
                'quoteQty' (float),
                'time' (unix timestamp),
                'isBuyerMaker' (bool)
            }
        ]
    """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/historicalTrades' if base_url == BASE_URL_FUTURES else '/api/v3/historicalTrades'
    params = {'symbol': pair.upper(), 'limit': limit}
    if fromId != None:
        params['fromId'] = fromId
    trades = send_public_request(base_url, url_path, params)
    # Convert str to float
    for trade in trades:
        trade['price'] = np.float64(trade['price'])
        trade['qty'] = np.float64(trade['qty'])
        trade['quoteQty'] = np.float64(trade['quoteQty'])
    return trades


def get_klines(market: str, pair: str, intervals: str, startTime=None, endTime=None, limit=1500):
    """
    Get candlestick bars (called klines) for a symbol. Klines are uniquely identified by their open time.
    If startTime and endTime are not sent, the most recent klines are returned.

    Arguments:
        pair (str): single pair
        intervals (list): timeframes to get candlesticks data
            ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        startTime (unix timestamp): start time in ms unix timestamp (inclusive)
        endTime (unix timestamp): end time in ms unix timestamp (inclusive)
        limit (int): less or equal to 1500

    Response:
        list of lists [
            [
                Open Time (ms unix timestamp)
                Open Price (float)
                High Price (float)
                Low Price (float)
                Close Price (float)
                Volume (float)
                Close Time (ms unix timestamp)
                Quote asset volume (float)
                Number of trades (int)
                Taker buy base asset volume (float)
                Taker buy quote asset volume (float)
            ]
        ]
    """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/klines' if base_url == BASE_URL_FUTURES else '/api/v3/klines'
    params = {'symbol': pair.upper(), 'interval': intervals, 'limit': limit}
    if startTime != None:
        params['startTime'] = startTime
    if endTime != None:
        params['endTime'] = endTime
    klines = send_public_request(base_url, url_path, params)
    # Convert str to float
    for i in range(len(klines)):
        klines[i] = [
            klines[i][0],
            np.float64(klines[i][1]),
            np.float64(klines[i][2]),
            np.float64(klines[i][3]),
            np.float64(klines[i][4]),
            np.float64(klines[i][5]),
            klines[i][6],
            np.float64(klines[i][7]),
            klines[i][8],
            np.float64(klines[i][9]),
            np.float64(klines[i][10]),
        ]
    return klines


def get_contract_klines(pair: str, intervals: str, contractType='PERPETUAL', startTime=None, endTime=None, limit=1500):
    """
    Get candlestick bars (called klines) for a specific contract type and symbol. Klines are uniquely identified by their open time.
    If startTime and endTime are not sent, the most recent klines are returned.

    Arguments:
        pair (str): single pair
        intervals (list): timeframes to get candlesticks data
            ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        contractType (list): valid contract types are [PERPETUAL, CURRENT_MONTH, NEXT_MONTH, CURRENT_QUARTER, NEXT_QUARTER]
        startTime (unix timestamp): start time in ms unix timestamp (inclusive)
        endTime (unix timestamp): end time in ms unix timestamp (inclusive)
        limit (int): less or equal to 1500

    Response:
        list of lists [
            [
                Open Time (ms unix timestamp)
                Open Price (float)
                High Price (float)
                Low Price (float)
                Close Price (float)
                Volume (float)
                Close Time (ms unix timestamp)
                Quote asset volume (float)
                Number of trades (int)
                Taker buy base asset volume (float)
                Taker buy quote asset volume (float)
            ]
        ]
    """
    base_url = BASE_URL_FUTURES
    url_path = '/fapi/v1/continuousKlines'
    params = {'pair': pair.upper(), 'interval': intervals, 'limit': limit, 'contractType': contractType}
    if startTime != None:
        params['startTime'] = startTime
    if endTime != None:
        params['endTime'] = endTime
    klines = send_public_request(base_url, url_path, params)
    # Convert str to float
    for i in range(len(klines)):
        klines[i] = [
            klines[i][0],
            np.float64(klines[i][1]),
            np.float64(klines[i][2]),
            np.float64(klines[i][3]),
            np.float64(klines[i][4]),
            np.float64(klines[i][5]),
            klines[i][6],
            np.float64(klines[i][7]),
            klines[i][8],
            np.float64(klines[i][9]),
            np.float64(klines[i][10]),
        ]
    return klines


def get_price(market: str, pair: str):
    """
    Get latest price for a symbol.

    Arguments:
        pair (str): single pair
    
    Response:

    """
    base_url = BASE_URL_FUTURES if market == 'futures' else BASE_URL_SPOT
    url_path = '/fapi/v1/ticker/price' if base_url == BASE_URL_FUTURES else '/api/v3/ticker/price'
    params = {'symbol': pair}
    ticker = send_public_request(base_url, url_path, params)
    price = np.float64(ticker['price'])
    return price