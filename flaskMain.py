from flask import Flask, jsonify, request, session
import pprint
from binance.client import Client
from binance import BinanceSocketManager
from binance.enums import *

testnet_key = 'your_key'
testnet_secret_key = 'your_secret_key'

client = Client(testnet_key, testnet_secret_key, testnet=True)

app = Flask(__name__)

@app.route('/openLimitOrder', methods=['POST'])
def open_limit_order():
    try:


        symbol = request.form.get("symbol")
        symbol_info = client.get_symbol_info(symbol)

        for filter in symbol_info['filters']:
            if filter['filterType'] == 'PERCENT_PRICE':
                multiplierDown = float(filter['multiplierDown'])
                multiplierUp = float(filter['multiplierUp'])

        get_avg_price = client.get_avg_price(symbol=symbol)
        avg_price = float(get_avg_price['price'])
        print('avg_price: ', avg_price)

        print('symbol: ' + symbol[:-4])
        balance = client.get_asset_balance(asset=symbol[:-4])
        freeQty = float(balance['free'])
        print('freeQty: ', freeQty)
        quantity = float(request.form.get("quantity"))
        print('quantity: ', quantity)
        price = float(request.form.get("price"))
        print('price: ', price)
        multiplication = quantity * price
        print('multiplication: ', multiplication)


        minQty = float(symbol_info['filters'][2]['minQty'])
        print('minQty: ', minQty)
        maxQty = float(symbol_info['filters'][2]['maxQty'])
        print('maxQty: ', maxQty)

        if request.form.get("side") == "buy":
            side = SIDE_BUY
        elif request.form.get("side") == "sell":
            side = SIDE_SELL
        print('side: ', side)


        if side == SIDE_BUY:
            if (multiplication > 10) and (quantity > minQty) and (quantity < maxQty) and (avg_price*multiplierUp >= price) and (avg_price*multiplierDown <= price):
                order = client.create_order(
                    symbol=symbol,
                    side=side,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=price
                )
                pprint.pprint(order)
                return jsonify({'status': 'order placed'})
            elif (avg_price*multiplierUp <= price) or (avg_price*multiplierDown >= price):
                return jsonify({'status': 'PRICE FILTER ERROR'})
            else:
                return jsonify({'status': 'doesnt meet requirements'})
        elif side == SIDE_SELL:
            if (quantity < freeQty) and (quantity > minQty) and (quantity < maxQty) and (avg_price*multiplierUp >= price) and (avg_price*multiplierDown <= price):
                order = client.create_order(
                    symbol=symbol,
                    side=side,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=price
                )
                pprint.pprint(order)
                return jsonify({'status': 'order placed'})
            elif (avg_price*multiplierUp <= price) or (avg_price*multiplierDown >= price):
                return jsonify({'status': 'PRICE FILTER ERROR'})
            else:
                return jsonify({'status': 'doesnt meet requirements'})



    except Exception as E:
        print(f"[AN ERROR HAS OCCURRED WITH :]{E}")



if __name__ == '__main__':
    app.run(debug=True)