from flask import Flask, jsonify, request, session
import pprint
from binance.client import Client
from binance.enums import *
import asyncio
from binance import AsyncClient, BinanceSocketManager
import database
import json
import config

testnet_key = config.testnet_key
testnet_secret_key = config.testnet_secret_key

client = Client(testnet_key, testnet_secret_key, testnet=True)

connection = database.connect_sql()

app = Flask(__name__)

@app.route('/openLimitOrder', methods=['POST'])
def open_limit_order():
    try:
        user_id = request.form.get("user_id")
        wallet_amount = json.loads(database.get_wallet_amount(connection=connection, user_id=user_id))
        print('Wallet: ', wallet_amount)


        symbol = request.form.get("symbol")
        print('symbol: ',symbol)
        asset = symbol[:-4]
        cash = symbol[-4:]
        print('asset: ', asset)
        print('cash: ', cash)
        symbol_info = client.get_symbol_info(symbol)
        """symbols = ['BTCBUSD','XRPBUSD','TRXBUSD']
        for symbol in symbols:
            orders = client.get_all_orders(symbol=symbol)"""
        for filter in symbol_info['filters']:
            if filter['filterType'] == 'PERCENT_PRICE':
                multiplierDown = float(filter['multiplierDown'])
                multiplierUp = float(filter['multiplierUp'])

        print("**************************************")
        for asset_type in wallet_amount['amounts']:
            if asset_type[0] == asset:
                wallet_amount_asset = float(asset_type[1])
            elif asset_type[0] == cash:
                wallet_amount_cash = float(asset_type[1])

        #wallet_amount_cash = wallet_amount['amounts'][0][1]
        print('NE KADAR CASHI VAR: ',wallet_amount_cash)
        #wallet_amount_asset = wallet_amount['amounts'][0][0]
        print('NE KADAR ASSETI VAR: ',wallet_amount_asset)
        print("???????????????????????????????????????????")





        get_avg_price = client.get_avg_price(symbol=symbol)
        print('GET_AVG_PRICE FONKSIYONU: ',get_avg_price)
        avg_price = float(get_avg_price['price'])
        print('avg_price: ', avg_price)


        print('symbol: ' + asset)
        balance = client.get_asset_balance(asset=asset)
        freeQty = float(balance['free'])
        print('freeQty: ', freeQty)
        quantity = float(request.form.get("quantity"))
        print('quantity: ', quantity)
        price = float(request.form.get("price"))
        print('price: ', price)
        transaction_amount_cash = quantity * price
        print('transaction_amount_cash: ', transaction_amount_cash)


        minQty = float(symbol_info['filters'][2]['minQty'])
        print('minQty: ', minQty)
        maxQty = float(symbol_info['filters'][2]['maxQty'])
        print('maxQty: ', maxQty)

        if request.form.get("side") == "buy":
            side = SIDE_BUY
        elif request.form.get("side") == "sell":
            side = SIDE_SELL
        print('side: ', side)
        print(avg_price)
        print(multiplierUp)
        print(multiplierDown)

        print(avg_price*multiplierUp)
        print(avg_price*multiplierDown)
        print(price)

        if side == SIDE_BUY:
            if (transaction_amount_cash >= 10.0) and transaction_amount_cash <= wallet_amount_cash and (quantity > minQty) and (quantity < maxQty):
                #PRICE FILTER KONTROLÜ HATALI OLDUĞU İÇİN ŞU KISMI SİLDİM: and (avg_price*multiplierUp >= price) and (avg_price*multiplierDown <= price)
                print('symbol: ', symbol)
                print('side: ', side)
                print('quantity: ',quantity)
                print('price: ', price)
                order = client.create_order(
                    symbol=symbol,
                    side=side,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=price
                )
                pprint.pprint(order)
                order_id = order['orderId']
                print(order_id)
                cursor = connection.cursor(buffered=True)
                cursor.execute(
                    "INSERT INTO transactions (fk_user_id,order_id,transaction_symbol) VALUES(%s,%s,%s)",
                    (user_id, order_id, symbol))
                connection.commit()
                #deposit_asset_database = database.deposit_amount(connection=connection, user_id=user_id, symbol=asset, amount=quantity)
                #withdraw_cash_database = database.withdraw_amount(connection=connection,user_id=user_id,symbol=cash,amount=transaction_amount_cash)
                """transaction = database.make_transaction(connection=connection,user_id=user_id,sold_symbol=cash,buy_quantity=quantity,buy_price=price,buy_symbol=asset)
                if transaction:
                    return jsonify({'status': 'order placed'})
                else:
                    return jsonify({'status': 'database error'})"""
                return jsonify({'status': 'order placed'})
            #elif (avg_price*multiplierUp <= price) or (avg_price*multiplierDown >= price):
                #return jsonify({'status': 'PRICE FILTER ERROR'})
            else:
                return jsonify({'status': 'doesnt meet requirements'})
        elif side == SIDE_SELL:
            if (transaction_amount_cash >= 10.0) and quantity <= wallet_amount_asset and (quantity <= freeQty) and (quantity > minQty) and (quantity < maxQty) and (avg_price*multiplierUp >= price) and (avg_price*multiplierDown <= price):
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
                return jsonify({'status': 'does not meet requirements'})



    except Exception as E:
        print(f"[AN ERROR HAS OCCURRED WITH :]{E}")

@app.route('/openMarketOrder', methods=['POST'])
def open_market_order():
    try:
        allcoins_info = client.get_all_tickers()

        symbol = request.form.get("symbol")
        asset = symbol[:-4]
        symbol_info = client.get_symbol_info(symbol)


        print('symbol: ' + asset)
        balance = client.get_asset_balance(asset=asset)
        freeQty = float(balance['free'])
        print('freeQty: ', freeQty)
        quantity = float(request.form.get("quantity"))
        print('quantity: ', quantity)
        #multiplication = quantity * price
        #print('multiplication: ', multiplication)

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
            if (quantity > minQty) and (quantity < maxQty):
                for coin in allcoins_info:
                    if coin['symbol'] == symbol:
                        coin_price = float(coin['price'])
                        print('coin price: ', coin_price)
                if coin_price*quantity >= 10.0:
                    order = client.create_order(
                        symbol=symbol,
                        side=SIDE_BUY,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity,
                    )
                    pprint.pprint(order)
                    return jsonify({'status': 'order placed'})
                else:
                    return jsonify({'status': 'must bid at least 10 dollar worth of coins'})
            else:
                return jsonify({'status': 'does not meet requirements'})
        elif side == SIDE_SELL:
            if (quantity < freeQty) and (quantity > minQty) and (quantity < maxQty):
                for coin in allcoins_info:
                    if coin['symbol'] == symbol:
                        coin_price = float(coin['price'])
                        print('coin price: ', coin_price)
                    pprint.pprint(coin)
                if coin_price * quantity >= 10.0:
                    order = client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity,
                    )
                    pprint.pprint(order)
                    return jsonify({'status': 'order placed'})
                else:
                    return jsonify({'status': 'must bid at least 10 dollar worth of coins'})
            else:
                return jsonify({'status': 'does not meet requirements'})

    except Exception as E:
        print(f"[AN ERROR HAS OCCURRED WITH :]{E}")

@app.route('/checkOrder', methods=['GET'])
def check_order_flask():
    user_id = request.form.get('user_id')
    print(user_id)
    results = database.check_order_database(connection=connection, user_id=user_id)
    for result in results:
        order_id = result[0]
        print(order_id)
        symbol = result[1]
        print(symbol)
        order = client.get_order(
            symbol=symbol,
            orderId=order_id)
        pprint.pprint(order)
        asset = symbol[:-4]
        cash = symbol[-4:]
        quantity = float(order['origQty'])
        if order['fills'][0]:
            price = float(order['fills'][0]['price'])
            print('FILLS PRICE: ', price)
        else:
            price = float(order['price'])
            print('FILLS DIŞI PRICE: ', price)
            print("")

    if order['status'] == 'FILLED' and order['symbol'] == 'BTCBUSD' and order['orderId'] == order_id:
        if order['side'] == 'BUY':
            transaction = database.make_transaction(connection=connection, user_id=user_id, sold_symbol=cash,
                                                    buy_quantity=quantity, buy_price=price, buy_symbol=asset)
            if transaction:
                return jsonify({'status': 'check_order_flask buy transaction success'})
            else:
                return jsonify({'status': 'check_order_flask buy transaction failure'})
        elif order['side'] == 'SELL':
            transaction = database.make_transaction(connection=connection, user_id=user_id, sold_symbol=asset,
                                                    buy_quantity=quantity, buy_price=price, buy_symbol=cash)
            if transaction:
                return jsonify({'status': 'check_order_flask sell transaction success'})
            else:
                return jsonify({'status': 'check_order_flask sell transaction failure'})

    else:
        return jsonify({'status': 'Not Filled'})





@app.route('/login', methods=['POST'])
def login():
    """
        There is a security vulnerability here due to
        login check with a simple boolean value dont use it
        on real life applications. Request can be simply intercepted
        and response can be manipulated as true instead of false :)
    """
    cnx = database.connect_sql()
    username = request.form.get('username')
    print(username)
    password = request.form.get('password')
    print(password)
    login_status = json.loads(database.login_check(cnx, username=username, password=password))
    if login_status['info'] == "access denied":
        return login_status
        cnx.close()
    else:
        session['id'] = login_status['info']['user_id']
        print(session.get('id'))
        return jsonify({"login":login_status})


@app.route('/register', methods=['POST'])
def register():
    cnx = database.connect_sql()
    username = request.form.get('register_user')
    password = request.form.get('register_pass')
    register_status = database.register_user(cnx, username=username, password=password)
    cnx.close()
    return register_status


@app.route('/changepass', methods=['POST'])
def change_pass():
    cnx = database.connect_sql()
    user_id = session.get('id')
    old_pass = request.form.get('old_pass')
    new_pass = request.form.get('new_pass')
    change_pass_status = database.update_pass(cnx, user_id=user_id, old_pass=old_pass, new_pass=new_pass)
    cnx.close()
    return change_pass_status



if __name__ == '__main__':
    app.run(debug=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_instant_price())