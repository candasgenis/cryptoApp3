from flask import Flask, jsonify, request, session
import pprint
from binance.client import Client
from binance import BinanceSocketManager
from binance.enums import *

testnet_key = 'your_testnet_key'
testnet_secret_key = 'your_testnet_secret_key'

client = Client(testnet_key, testnet_secret_key, testnet=True)

app = Flask(__name__)

@app.route('/openLimitOrder', methods=['POST'])
def open_limit_order():
    try:
        account_info = client.get_account()

        symbol = request.form.get("symbol")
        symbol_info = client.get_symbol_info(symbol)

        isInWallet = False

        for asset in account_info['balances']:
            symbol_in_wallet = asset['asset']
            #print(symbol_in_wallet)
            if symbol[:-4] == symbol_in_wallet:
                print(symbol_in_wallet)
                isInWallet = True
                freeQty = float(asset['free'])
        if isInWallet == False:
            return jsonify({'status': 'You dont have this symbol in your wallet'})
        quantity = request.form.get("quantity")
        print(quantity)
        price = request.form.get("price")
        print(price)
        multiplication = float(quantity) * float(price)
        print(multiplication)


        minQty = float(symbol_info['filters'][2]['minQty'])
        print(minQty)
        maxQty = float(symbol_info['filters'][2]['maxQty'])
        print(maxQty)

        if request.form.get("side") == "buy":
            side = SIDE_BUY
        elif request.form.get("side") == "sell":
            side = SIDE_SELL
        print(side)

        if side == SIDE_BUY:
            if (multiplication > 10) and (float(quantity) > minQty) and (float(quantity) < maxQty):
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
            else:
                return jsonify({'status': 'doesnt meet requirements'})
        elif side == SIDE_SELL:
            if ((float(quantity) < freeQty) and (float(quantity) > minQty) and (float(quantity) < maxQty)):
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
            else:
                return jsonify({'status': 'doesnt meet requirements'})



    except Exception as E:
        print(f"[AN ERROR HAS OCCURRED WITH :]{E}")



if __name__ == '__main__':
    app.run(debug=True)