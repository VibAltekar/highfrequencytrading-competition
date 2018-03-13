import sys
import socket
import json
import bot
env = sys.argv[1]

if str(env) == "p":
    env = "production"
else:
    env = "test-exch-KPCBTRAPHOUSE"



def connect(serv_addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serv_addr, int(port)))
    return (s, s.makefile('rw', 1))

s, exchange = connect(env,25000)
json_string = '{"type": "hello", "team":"KPCBTRAPHOUSE"}'
print(json_string, file=exchange)

f = open('goog_log.txt', 'w')

trade_counter = 1
owned_bond_shares = 0

GOOG_buy_price = 0
GOOG_best_price = 0
GOOG_prices_count = 0
GOOG_shares_owned = 0
GOOG_min_buy_price = 0
MSFT_buy_price = 0
MSFT_best_price = 0
MSFT_prices_count = 0
MSFT_shares_owned = 0
MSFT_min_buy_price = 0
AAPL_buy_price = 0
AAPL_best_price = 0
AAPL_prices_count = 0
AAPL_shares_owned = 0
AAPL_min_buy_price = 0

volatility = 2
observance = 2
stock_max = 10

while (True):
    hello_from_exchange = exchange.readline().strip()
    msg = json.loads(hello_from_exchange)
    if (msg["type"] == "book" and msg["symbol"] == "GOOG"):
        if (msg["sell"] and GOOG_prices_count < observance):
            GOOG_min_buy_price = min(GOOG_min_buy_price, msg["sell"][0][0])
            GOOG_prices_count += 1
        if (msg["sell"] and msg["sell"][0][0] <= GOOG_min_buy_price and GOOG_shares_owned + msg["sell"][0][1] < stock_max):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "GOOG", "dir" : "BUY", "price" : msg["sell"][0][0], "size" : msg["sell"][0][1]}
            GOOG_buy_price = msg["sell"][0][0]
            f.write("GOOG Buy: " + str(msg["sell"][0][1]) + " @ " + str(GOOG_buy_price) + "\n")
            GOOG_best_price = max(GOOG_buy_price, GOOG_best_price)
            print(json.dumps(json_string), file=exchange)
            GOOG_shares_owned += msg["sell"][0][1]
            GOOG_prices_count += 1
        if (msg["buy"]):
            if (GOOG_shares_owned > 0 and msg["buy"][0][0] > GOOG_best_price):
                json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "GOOG", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : min(msg["buy"][0][1], GOOG_shares_owned)}
                GOOG_shares_owned -= msg["buy"][0][1]
                f.write("GOOG Sell: " + str(msg["buy"][0][0]) + ", " + str(GOOG_shares_owned) + ", left \n")
                print(json.dumps(json_string), file=exchange)
    if (msg["type"] == "book" and msg["symbol"] == "MSFT"):
        if (msg["sell"] and MSFT_prices_count < observance):
            MSFT_min_buy_price = min(MSFT_min_buy_price, msg["sell"][0][0])
        if (msg["sell"] and msg["sell"][0][0] <= MSFT_min_buy_price and MSFT_shares_owned + msg["sell"][0][1] < stock_max):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "MSFT", "dir" : "BUY", "price" : msg["sell"][0][0], "size" : msg["sell"][0][1]}
            MSFT_buy_price = msg["sell"][0][0]
            f.write("MSFT Buy: " + str(msg["sell"][0][1]) + " @ " + str(MSFT_buy_price) + "\n")
            MSFT_best_price = max(MSFT_buy_price, MSFT_best_price)
            print(json.dumps(json_string), file=exchange)
            MSFT_shares_owned += msg["sell"][0][1]
            MSFT_prices_count += 1
        if (msg["buy"]):
            if (MSFT_shares_owned > 0 and msg["buy"][0][0] > MSFT_best_price):
                json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "MSFT", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : min(msg["buy"][0][1], MSFT_shares_owned)}
                MSFT_shares_owned -= msg["buy"][0][1]
                f.write("MSFT Sell: " + str(msg["buy"][0][0]) + ", " + str(MSFT_shares_owned) + ", left \n")
                print(json.dumps(json_string), file=exchange)
    if (msg["type"] == "book" and msg["symbol"] == "AAPL"):
        if (msg["sell"] and AAPL_prices_count < observance):
            AAPL_min_buy_price = min(AAPL_min_buy_price, msg["sell"][0][0])
        if (msg["sell"] and msg["sell"][0][0] <= AAPL_min_buy_price and AAPL_shares_owned + msg["sell"][0][1] < stock_max):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "AAPL", "dir" : "BUY", "price" : msg["sell"][0][0], "size" : msg["sell"][0][1]}
            AAPL_buy_price = msg["sell"][0][0]
            f.write("AAPL Buy: " + str(msg["sell"][0][1]) + " @ " + str(AAPL_buy_price) + "\n")
            AAPL_best_price = max(AAPL_buy_price, AAPL_best_price)
            print(json.dumps(json_string), file=exchange)
            AAPL_shares_owned += msg["sell"][0][1]
            AAPL_prices_count += 1
        if (msg["buy"]):
            if (AAPL_shares_owned > 0 and msg["buy"][0][0] > AAPL_best_price):
                json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "AAPL", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : min(msg["buy"][0][1], AAPL_shares_owned)}
                AAPL_shares_owned -= msg["buy"][0][1]
                f.write("AAPL Sell: " + str(msg["buy"][0][0]) + ", " + str(AAPL_shares_owned) + ", left \n")
                print(json.dumps(json_string), file=exchange)
    if (msg["type"] == "ack"):
        continue
        #f.write("trade " + str(msg["order_id"]) + "\n")
    print(msg, file = sys.stderr)
