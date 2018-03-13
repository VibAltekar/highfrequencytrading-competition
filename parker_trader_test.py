import sys
import socket
import json
import time
env = sys.argv[1]

if str(env) == "p":
    env = "production"
else:
    env = "test-exch-KPCBTRAPHOUSE"

f = open('parkerlog.txt', 'w')

def connect(serv_addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serv_addr, int(port)))
    return (s, s.makefile('rw', 1))

s, exchange = connect(env, 25000)
json_string = '{"type": "hello", "team":"KPCBTRAPHOUSE"}'
print(json_string, file=exchange)

f = open('log.txt', 'w')

trade_counter = 1
owned_bond_shares = 0

buy_dict = {}
sell_dict = {}

NOKFH_BUY = NOKUS_BUY = NOKFH_SELL = NOKUS_SELL = 0
BOND_SHARE = MSFT_SHARE = AAPL_SHARE = GOOG_SHARE = XLK_SHARE = 0

def Convert(NOKUS_PRICE, NOKUS_QUANT, NOKFH_PRICE, NOKFH_QUANT):
    PRICE_DIFF = NOKUS_PRICE - NOKFH_PRICE
    MIN_QUANT = min(NOKUS_QUANT, NOKFH_QUANT)
    MONEY_DIFF = MIN_QUANT * PRICE_DIFF
    if MONEY_DIFF > 11:
        # TODO: meaning NOKFH is cheaper! buy in NOKFH and sell NOKUS with the minimum quantity
        return 1
    elif MONEY_DIFF < -11:
        # TODO: meaning NOKUS is cheaper! buy in NOKUS and sell NOKFH with the minimum quantity
        return 0

order_info = {}

def store_order(order_id, stock_name, quantity, buyorsell):
    if buyorsell == 'BUY':
        order_info[order_id] = [stock_name, quantity]
    elif buyorsell == 'SELL':
        order_info[order_id] = [stock_name, -quantity]

def reject(order_id):
    list = order_info[order_id]
    stock_name = list[0]; quantity = list[1]
    if stock_name == 'BOND':
        BOND_SHARE -= quantity
    elif stock_name == 'MSFT':
        MSFT_SHARE -= quantity
    elif stock_name == 'GOOG':
        GOOG_SHARE -= quantity
    elif stock_name == 'AAPL':
        AAPL_SHARE -= quantity

while (True):
    time.sleep(0.02)
    hello_from_exchange = exchange.readline().strip()
    msg = json.loads(hello_from_exchange)
    # print(msg)
    if (msg["type"] == "book"):
        try:
            buy_dict[msg["symbol"]] = msg["buy"][0][0]
            sell_dict[msg["symbol"]] = msg["sell"][0][0]
        except IndexError:
            pass

    if len(buy_dict.keys()) < 7 or len(sell_dict.keys()) < 7:
        continue

    if (msg['type'] == 'reject'):
        print(msg)
        reject(msg['order_id'])
    # ETF Trading

    if (msg["type"] == "book" and (msg["symbol"] == "BOND" or "AAPL" or 'MSFT' or 'GOOG' or 'XLK')):
        BOND_AVG = (buy_dict["BOND"] + sell_dict["BOND"]) / 2
        AAPL_AVG = (buy_dict["AAPL"] + sell_dict["AAPL"]) / 2
        MSFT_AVG = (buy_dict["MSFT"] + sell_dict["MSFT"]) / 2
        GOOG_AVG = (buy_dict["GOOG"] + sell_dict["GOOG"]) / 2
        XLK_AVG = (buy_dict["XLK"] + sell_dict["XLK"]) / 2

        ADDGREGATE = 3 * BOND_AVG + 3 * MSFT_AVG + 2 * AAPL_AVG + 2 * GOOG_AVG
        DIFF = ADDGREGATE - 10 * XLK_AVG
        print(DIFF)



        # TODO: the conversion when I reach the 100 or -100 shares limit
        print(BOND_SHARE, MSFT_SHARE, AAPL_SHARE, GOOG_SHARE, XLK_SHARE)

        if BOND_SHARE > 90 or MSFT_SHARE > 90 or AAPL_SHARE > 90 or GOOG_SHARE > 90 or XLK_SHARE < -90:
            # convert
            json_string = {"type": "convert", "order_id": trade_counter, "symbol": "XLK", "dir": "BUY", "size": 50}
            print(json.dumps(json_string), file=exchange)
            BOND_SHARE -= 15; MSFT_SHARE -= 15; AAPL_SHARE -= 10; GOOG_SHARE -= 10; XLK_SHARE += 50
            trade_counter += 1

        if BOND_SHARE < -90 or MSFT_SHARE < -90 or AAPL_SHARE < -90 or GOOG_SHARE < -90 or XLK_SHARE > 80:
            # convert
            json_string = {"type": "convert", "order_id": trade_counter, "symbol": "XLK", "dir": "SELL", "size": 50}
            print(json.dumps(json_string), file=exchange)
            BOND_SHARE += 15; MSFT_SHARE += 15; AAPL_SHARE += 10; GOOG_SHARE += 10; XLK_SHARE -= 50
            trade_counter += 1




        if DIFF < -100:
            # meaning the aggregate is cheaper and sell as XLK_AVG
            # buy 3 shares of BOND
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "BOND", "dir": "BUY", "price": buy_dict['BOND'], "size": 3}
            print(json.dumps(json_string), file=exchange)
            BOND_SHARE += 3
            store_order(trade_counter, 'BOND', 3, "BUY")
            trade_counter += 1
            # buy 3 shares of MSFT
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "MSFT", "dir": "BUY", "price": buy_dict['MSFT'], "size": 3}
            print(json.dumps(json_string), file=exchange)
            MSFT_SHARE += 3
            store_order(trade_counter, 'MSFT', 3, "BUY")
            trade_counter += 1
            # buy 2 shares of AAPL
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "AAPL", "dir": "BUY", "price": buy_dict['AAPL'], "size": 2}
            print(json.dumps(json_string), file=exchange)
            AAPL_SHARE += 2
            store_order(trade_counter, 'AAPL', 2, "BUY")
            trade_counter += 1
            # buy 2 shares of GOOG
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "GOOG", "dir": "BUY", "price": buy_dict['GOOG'], "size": 2}
            print(json.dumps(json_string), file=exchange)
            GOOG_SHARE += 2
            store_order(trade_counter, 'GOOG', 2, "BUY")
            trade_counter += 1
            # sell 10 shares of XLK
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "XLK", "dir": "SELL", "price": sell_dict['XLK'], "size": 10}
            print(json.dumps(json_string), file=exchange)
            XLK_SHARE -= 10
            store_order(trade_counter, 'XLK', 10, "SELL")
            trade_counter += 1


        elif DIFF > 100:
            # meaning the XLK is cheaper and buy in XLK_AVG and sell as individual stocks
            # buy 10 shares of XLK
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "XLK", "dir": "BUY", "price": buy_dict['XLK'], "size": 10}
            print(json.dumps(json_string), file=exchange)
            XLK_SHARE += 10
            store_order(trade_counter, 'XLK', 10, "BUY")
            trade_counter += 1
            # sell 3 shares of BOND
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "BOND", "dir": "SELL", "price": sell_dict['BOND'], "size": 3}
            print(json.dumps(json_string), file=exchange)
            BOND_SHARE -= 3
            store_order(trade_counter, 'BOND', 3, "SELL")
            trade_counter += 1
            # sell 3 shares of MSFT
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "MSFT", "dir": "SELL", "price": sell_dict['MSFT'], "size": 3}
            print(json.dumps(json_string), file=exchange)
            MSFT_SHARE -= 3
            store_order(trade_counter, 'MSFT', 3, "SELL")
            trade_counter += 1
            # sell 2 shares of AAPL
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "AAPL", "dir": "SELL", "price": sell_dict['AAPL'], "size": 2}
            print(json.dumps(json_string), file=exchange)
            AAPL_SHARE -= 2
            store_order(trade_counter, 'AAPL', 2, "SELL")
            trade_counter += 1
            # sell 2 shares of GOOG
            json_string = {"type": "add", "order_id": trade_counter, "symbol": "GOOG", "dir": "SELL", "price": sell_dict['GOOG'], "size": 2}
            print(json.dumps(json_string), file=exchange)
            GOOG_SHARE -= 2
            store_order(trade_counter, 'GOOG', 2, "SELL")
            trade_counter += 1



    # ADR Trading
    #
    # if (msg["type"] == "book" and (msg["symbol"] == "NOKFH" or msg["symbol"] == "NOKUS")):
    #     if (msg["sell"] and msg["buy"] and msg["symbol"] == "NOKFH"):
    #         NOKFH_BUY = msg["sell"][0][0]
    #         NOKFH_SELL = msg["buy"][0][0]
    #     if (msg["sell"] and msg["buy"] and msg["symbol"] == "NOKUS"):
    #         NOKUS_BUY = msg["sell"][0][0]
    #         NOKUS_SELL = msg["buy"][0][0]
    #     if (msg["sell"] and NOKUS_SELL != 0 and NOKFH_BUY + 10 < NOKUS_SELL):
    #         # Buy NOKFH, convert, sell NOKUS
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "BUY", "price" : NOKFH_BUY, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("buy NOKFH at " + str(NOKFH_BUY) + "\n")
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "BUY", "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "SELL", "price" : NOKUS_SELL, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("sell NOKUS at " + str(NOKUS_SELL) + "\n")
    #     elif (msg["buy"] and NOKFH_SELL != 0 and NOKUS_BUY + 10 < NOKFH_SELL):
    #         # Buy NOKUS, convert, sell NOKFH
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "BUY", "price" : NOKUS_BUY, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("buy NOKUS at " + str(NOKUS_BUY) + "\n")
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "BUY", "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "SELL", "price" : NOKFH_SELL, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("sell NOKFH at " + str(NOKFH_SELL) + "\n")
    #
    # # Bond Trading
    # if (msg["type"] == "book" and msg["symbol"] == "BOND"):
    #     if (msg["sell"] and sell_dict['BOND'] < 1000 and owned_bond_shares + msg["sell"][0][1] < 100):
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "BOND", "dir" : "BUY", "price" : sell_dict['BOND'], "size" : msg["sell"][0][1]}
    #         owned_bond_shares += msg["sell"][0][1]
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("bought " + str(trade_counter) + " " + str(sell_dict['BOND']) + " " + str(msg["sell"][0][1]) + "\n")
    #         trade_counter += 1
    #     if (msg["buy"] and buy_dict["BOND"] > 1000 and owned_bond_shares > 0):
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "BOND", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : msg["buy"][0][1]}
    #         owned_bond_shares -= msg["buy"][0][1]
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("sold " + str(trade_counter) + " " + str(buy_dict["BOND"]) + " " + str(msg["buy"][0][1]) + "\n")
    #         trade_counter += 1

    print(msg, file = sys.stderr)



# TRASH


    # # if ('NOKFH' in buy_dict and 'NOKFH' in sell_dict and 'NOKUS' in buy_dict and 'NOKUS' in sell_dict):
    # if (msg["type"] == "book" and (msg["symbol"] == "NOKFH" or msg["symbol"] == "NOKUS")):
    #     # if (msg["sell"] and msg["buy"] and msg["symbol"] == "NOKFH"):
    #     #     NOKFH_BUY = sell_dict['NOKFH']
    #     #     NOKFH_SELL = buy_dict['NOKFH']
    #     # if (msg["sell"] and msg["buy"] and msg["symbol"] == "NOKUS"):
    #     #     NOKUS_BUY = sell_dict['NOKFH']
    #     #     NOKUS_SELL = buy_dict['NOKFH']
    #     if (msg["sell"] and NOKUS_SELL != 0 and NOKFH_BUY + 10 < NOKUS_SELL):
    #         # Buy NOKFH, convert, sell NOKUS
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "BUY", "price" : NOKFH_BUY, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("buy NOKFH at " + str(NOKFH_BUY) + "\n")
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "BUY", "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "SELL", "price" : NOKUS_SELL, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("sell NOKUS at " + str(NOKUS_SELL) + "\n")
    #     elif (msg["buy"] and NOKFH_SELL != 0 and NOKUS_BUY + 10 < NOKFH_SELL):
    #         # Buy NOKUS, convert, sell NOKFH
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "BUY", "price" : NOKUS_BUY, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("buy NOKUS at " + str(NOKUS_BUY) + "\n")
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "BUY", "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         trade_counter += 1
    #         json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "SELL", "price" : NOKFH_SELL, "size" : msg["sell"][0][1]}
    #         print(json.dumps(json_string), file=exchange)
    #         f.write("sell NOKFH at " + str(NOKFH_SELL) + "\n")

