import pprint
from binance.client import Client
from binance import BinanceSocketManager
from binance.enums import *

testnet_key = 'your_testnet_key'
testnet_secret_key = 'your_testnet_secret_key'

client = Client(testnet_key, testnet_secret_key, testnet=True)

#Market Data Endpoints
depth = client.get_order_book(symbol='XRPBUSD')
res = client.get_exchange_info()
time_res = client.get_server_time()
status = client.get_system_status()
symbol_info = client.get_symbol_info('BTCBUSD')
allcoins_info = client.get_all_tickers()
avg_price = client.get_avg_price(symbol='XRPBUSD')
prices = client.get_all_tickers()
orderbook_tickers = client.get_orderbook_tickers()

#Account Endpoints
account_info = client.get_account()
#open order
"""order = client.create_order(
    symbol='BTCBUSD',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=0.001,
    price=10000
    )"""
orders = client.get_all_orders(symbol='BTCBUSD')
#delete order
"""result = client.cancel_order(
    symbol='BTCBUSD',
    orderId='1787')"""
open_orders = client.get_open_orders(symbol='BTCBUSD')

#account_snapshot = client.get_account_snapshot(type='SPOT')


pprint.pprint(account_info)

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




