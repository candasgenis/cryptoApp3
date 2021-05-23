import mysql.connector
import yaml
import string
import random
import json
import pprint
from binance.client import Client
import config


"""
Register method return value is JSON 
Login method return value is Boolean
Update_pass method return value is JSON

"""
testnet_key = config.testnet_key
testnet_secret_key = config.testnet_secret_key

credentials = yaml.safe_load(open('./src/creds.yaml'))

client = Client(testnet_key, testnet_secret_key, testnet=True)

def id_generator(size, chars):
    return ''.join(random.choice(chars) for _ in range(size))


def connect_sql():
    try:
        connection = mysql.connector.connect(
            host=credentials['db_host'],
            database=credentials['db_database'],
            user=credentials['db_username'],
            password=credentials['db_password'],
            auth_plugin='mysql_native_password'
        )
        print("Connection established")
        return connection
    except Exception as E:
        print("Error with description :  {}".format(E))


def register_user(connection, username, password):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_name FROM users WHERE user_name=%s",(username,))
        result = cursor.fetchone()
        if result:
            return json.dumps({"info":"Already Exists"})
        else:
            user_id = id_generator(10, chars=string.ascii_uppercase + string.digits)
            wallet_id = id_generator(10, chars=string.ascii_uppercase + string.digits)
            pk_wallet = id_generator(10, chars=string.ascii_uppercase + string.digits)
            cursor.execute("INSERT INTO users(user_id,user_name,user_pass,user_wallet)VALUES(%s,%s,%s,%s)",
                           (user_id, username, password, wallet_id,))
            connection.commit()
            cursor.execute("INSERT INTO wallets(wallet_id,pk_wallet) VALUES(%s,%s)", (wallet_id,pk_wallet,))
            connection.commit()
            return json.dumps({"info": {'user_id':user_id, 'wallet_id':wallet_id}})
    except Exception as E:
        print("There is an error occured with (Make sure that you pass the connection object) : {}".format(E))


def login_check(connection, username, password):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_name=%s AND user_pass=%s", (username, password,))
        result = cursor.fetchone()
        if result:
            return json.dumps({"info": {"user_id": result[0], "user_name": username}})
        else:
            return json.dumps({"info":"access denied"})
    except Exception as E:
        print("Error: {}".format(E))


def update_pass(connection, user_id, old_pass, new_pass):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_pass FROM users WHERE user_id=%s", (user_id,))
        current_pass = cursor.fetchone()
        if current_pass[0] == old_pass:
            if current_pass[0] == new_pass:
                return json.dumps({"Status": "same_password"})
            else:
                cursor.execute("UPDATE users SET user_pass=%s WHERE user_id=%s", (new_pass, user_id,))
                connection.commit()
                return json.dumps({"status": "password_changed"})
        else:
            return json.dumps({"status": "invalid_password"})
    except Exception as E:
        print("Error :{}".format(E))


def get_wallet_amount(connection, user_id):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT wallet_symbol,wallet_quantity FROM wallets"
                       " WHERE wallet_id=(SELECT user_wallet FROM users WHERE user_id=%s)", (user_id,))
        result = cursor.fetchall()
        return json.dumps({"amounts": result})
    except Exception as E:
        print("Error: {}".format(E))


def deposit_amount(connection, user_id, symbol, amount):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT user_wallet FROM users WHERE user_id=%s", (user_id,))
        wallet_id = cursor.fetchone()[0]
        print("Wallet_id : {}".format(wallet_id))
        if amount > 0:
            cursor.execute("SELECT wallet_quantity,pk_wallet FROM wallets WHERE wallet_id=%s AND wallet_symbol=%s",
                           (wallet_id, symbol,))
            result = cursor.fetchone()
            if result:
                new_amount = result[0] + amount
                primary_key = result[1]
                cursor.execute("UPDATE wallets SET wallet_quantity=%s WHERE pk_wallet=%s"
                               ,(new_amount, primary_key))
                connection.commit()
                return json.dumps({"transaction": [{"amount": amount,
                                                    "updated_amount":new_amount,
                                                    "symbol": symbol,
                                                    "wallet_id": wallet_id,
                                                    "status": "updated"}]})
            ##
            else:
                pk_wallet = id_generator(10, chars=string.ascii_uppercase + string.digits)
                cursor.execute("INSERT INTO wallets (wallet_id,wallet_symbol,wallet_quantity,pk_wallet) VALUES(%s,%s,%s,%s)",
                               (wallet_id, symbol, amount, pk_wallet,))
                connection.commit()
                return json.dumps({"transaction":[{"amount": amount, "symbol": symbol, "wallet_id": wallet_id}]})
        else:
            return json.dumps({"error": "Deposit cant below 0 quantity"})

    except Exception as E:
        print("Error : {}".format(E))


def withdraw_amount(connection, user_id, symbol, amount):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT pk_wallet FROM wallets WHERE wallet_id=(SELECT user_wallet FROM users WHERE user_id=%s) AND wallet_symbol=%s",
                                (user_id, symbol))
        pk_wallet = cursor.fetchone()[0]

        cursor.execute("SELECT wallet_symbol,wallet_quantity FROM wallets WHERE pk_wallet=%s",(pk_wallet,))
        wallet_info = cursor.fetchone()
        if wallet_info:
            if wallet_info[1] - amount > 0:
                update_amount = wallet_info[1] - amount
                cursor.execute("UPDATE wallets SET wallet_quantity=%s WHERE pk_wallet=%s",(update_amount,pk_wallet))
                connection.commit()
                return json.dumps({"status": {"user_id": user_id, "symbol": symbol, "new_amount": update_amount , "sold": amount,
                                               "process": "update"}})

            elif wallet_info[1] - amount == 0:
                cursor.execute("DELETE FROM wallets WHERE pk_wallet=%s", (pk_wallet,))
                connection.commit()
                return json.dumps({"status": {"user_id": user_id, "symbol": symbol, "sold": amount,
                                               "process": "dump"}})
            else:
                return json.dumps({"status": "Quantity cannot be less than zero"}),
        else:
            print("No such record")


    except Exception as E:
        print("Error : {}".format(E))


"""def make_transaction(connection, user_id, sold_symbol, buy_quantity, buy_price, buy_symbol):
    try:
        cursor = connection.cursor(buffered=True)
        sql = "SELECT wallet_quantity,pk_wallet FROM wallets WHERE wallet_id=(SELECT user_wallet FROM users WHERE user_id=%s) AND wallet_symbol=%s OR wallet_symbol=%s"
        cursor.execute(sql, (user_id, 'USDT', 'BUSD'))
        result = cursor.fetchone()
        if result[0] >= buy_price * buy_quantity:
            result = json.loads(withdraw_amount(connection, user_id, sold_symbol, buy_price*buy_quantity))
            if result:
                deposit = json.loads(deposit_amount(connection, user_id, buy_symbol, result['status']['sold']))
                return deposit
        else:
            return json.dumps({"status": "Not enough quantity"})
    except Exception as E:
        print("Error : {}".format(E))"""

def buy_transaction(connection, user_id, sold_symbol, buy_symbol, buy_price, buy_quantity):
    cursor = connection.cursor(buffered=True)

    if sold_symbol == 'USDT':
        symbol = 'USDT'
    elif sold_symbol == 'BUSD':
        symbol = 'BUSD'
    else:
        symbol = "USDT"

    try:
        cursor.execute("SELECT wallet_quantity,pk_wallet FROM wallets WHERE(SELECT user_wallet FROM users WHERE user_id=%s) AND wallet_symbol=%s"
                                   , (user_id, symbol,))
        result = cursor.fetchone()
        print(result)
        if result:
            if result[0] >= buy_quantity * buy_price:
                withdraw_amount(connection, user_id, symbol, buy_quantity*buy_price)
                return_val = json.loads(deposit_amount(connection, user_id, buy_symbol, buy_quantity))
                return return_val
    except Exception as E:
        print("Error: {}".format(E))


def sell_transaction(connection, user_id, buy_symbol, sold_symbol, sold_price, sold_quantity):

    if buy_symbol == 'USDT':
        symbol = 'USDT'
    elif buy_symbol == 'BUSD':
        symbol = 'BUSD'
    else:
        symbol = "USDT"

    try:
        cursor = connection.cursor(buffered=True)

        cursor.execute(
            "SELECT wallet_quantity,pk_wallet FROM wallets WHERE(SELECT user_wallet FROM users WHERE user_id=%s) AND wallet_symbol=%s"
            , (user_id, sold_symbol,))
        result = cursor.fetchone()
        if result[0] >= sold_quantity:
            withdraw_amount(connection, user_id, sold_symbol, sold_quantity)
            return_val=json.loads(deposit_amount(connection, user_id, symbol, sold_quantity*sold_price))
            return return_val
    except Exception as E:
        print("Error: {}".format(E))

def get_account_info(connection, user_id):
    cursor = connection.cursor(buffered=True)
    coin_arr = []
    cursor.execute("SELECT user_wallet,user_name FROM users WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()
    wallet_id = result[0]
    user_name = result[1]
    print(wallet_id)
    cursor.execute("SELECT wallet_symbol,wallet_quantity FROM wallets WHERE wallet_id=%s", (wallet_id,))
    symbol_quantity = cursor.fetchall()
    for symbol in symbol_quantity:
        coin_arr.append({'symbol':symbol[0],'value':symbol[1]})
    return json.dumps({'wallet_id': wallet_id , 'user_name': user_name, 'coins': coin_arr, 'user_id': user_id})

def check_order_database(connection, user_id):
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT order_id, transaction_symbol FROM transactions WHERE fk_user_id=%s", (user_id,))
    result = cursor.fetchall()
    return result
def isFilled(connection, user_id):
    results = check_order_database(connection=connection, user_id=user_id)
    for result in results:
        order_id = result[0]
        print(order_id)
        symbol = result[1]
        print(symbol)
        order = client.get_order(
            symbol=symbol,
            orderId=order_id)
        pprint.pprint(order)
        if order['status'] == 'FILLED' and order['symbol'] == 'BTCBUSD' and order['orderId'] == order_id:
            return True
        else:
            return False
if __name__ == '__main__':
    cnx = connect_sql()
    #result = json.loads(login_check(cnx, "Kenan", "Test"))
    #print(result['info']['user_id'])
    #pprint.pprint(json.loads(deposit_amount(cnx, '9EG18NMP0V', 'BNBTRX', 20)))
    #pprint.pprint(json.loads(withdraw_amount(cnx, '9EG18NMP0V', 'BNBTRX', 20)))
    #pprint.pprint(make_transaction(cnx,'9EG18NMP0V','BNB', 100 , 1, 'USDT'))
    #pprint.pprint(register_user(connection=cnx,username='Candas',password='12345'))
    pprint.pprint(deposit_amount(connection=cnx,user_id='9EG18NMP0V',symbol='USDT',amount=100000))