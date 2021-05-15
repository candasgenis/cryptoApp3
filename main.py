import pprint
from binance.client import Client
from binance import BinanceSocketManager
from binance.enums import *
import time

testnet_key = 'your_key'
testnet_secret_key = 'your_secret_key'

class Binance:
    def __init__(self, public_key = testnet_key, secret_key = testnet_secret_key, sync = False):
        self.time_offset = 0
        self.b = Client(public_key, secret_key)
        self.b.API_URL = 'https://testnet.binance.vision/api' # for testnet

        if sync:
            self.time_offset = self._get_time_offset()
            print( "Offset: %s ms" % (self.time_offset) )

    def _get_time_offset(self):
        res = self.b.get_server_time()
        return res['serverTime'] - int(time.time() * 1000)

    def synced(self, fn_name, **args):
        args['timestamp'] = int(time.time() * 1000 + self.time_offset)
        return getattr(self.b, fn_name)(**args)


client = Client(testnet_key, testnet_secret_key, testnet=True)
my_binance = Binance(testnet_key, testnet_secret_key, True)
# my_binance.synced('order_market_buy',  symbol='BNBBTC', quantity=10)
account_info = my_binance.synced('get_account', recvWindow=60000)


#Market Data Endpoints
#depth = client.get_order_book(symbol='XRPBUSD')
#res = client.get_exchange_info()
#time_res = client.get_server_time()
#status = client.get_system_status()
symbol_info = client.get_symbol_info('XRPBTC')
#allcoins_info = client.get_all_tickers()
avg_price = client.get_avg_price(symbol='XRPBTC')
#prices = client.get_all_tickers()
#orderbook_tickers = client.get_orderbook_tickers()
#candles = client.get_klines(symbol='BTCBUSD', interval=Client.KLINE_INTERVAL_5MINUTE)

#Account Endpoints
#account_info = client.get_account()
#balance = client.get_asset_balance(asset='BTC')
#open order
"""order = client.create_order(
    symbol='BTCBUSD',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=0.001,
    price=10000
    )"""
#orders = client.get_all_orders(symbol='BTCBUSD')
#delete order
"""result = client.cancel_order(
    symbol='BTCBUSD',
    orderId='1787')"""
#open_orders = client.get_open_orders(symbol='BTCBUSD')

#account_snapshot = client.get_account_snapshot(type='SPOT')

for filter in symbol_info['filters']:
    if filter['filterType'] == 'PERCENT_PRICE':
        multiplierDown = float(filter['multiplierDown'])
        pprint.pprint(multiplierDown)
        multiplierUp = float(filter['multiplierUp'])
        pprint.pprint(multiplierUp)

pprint.pprint(avg_price)

"""for asset in account_info['balances']:
    symbol_in_wallet = asset['asset']
    print(symbol_in_wallet)"""

"""print(float(symbol_info['filters'][2]['minQty']))
print(float(symbol_info['filters'][2]['maxQty']))

if 0.0000000001 > float(symbol_info['filters'][2]['minQty']):
    print("yes")
else:
    print("no")"""

#pprint.pprint(open_orders)




