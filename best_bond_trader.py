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

f = open('log.txt', 'w')

trade_counter = 1
owned_bond_shares = 0

NOKFH_BUY = NOKUS_BUY = NOKFH_SELL = NOKUS_SELL = 0
count = 0
array = []
GOOG_owned = 0
GOOG_window_max = 0
GOOG_window_min = 0
GOOG_threshold = 1
GOOG_most_recent_min = 0

while (True):
    hello_from_exchange = exchange.readline().strip()
    msg = json.loads(hello_from_exchange)
    if (msg["type"] == "book" and (msg["symbol"] == "NOKFH" or msg["symbol"] == "NOKUS")):
        if (msg["sell"] and msg["buy"] and msg["symbol"] == "NOKFH"):
            NOKFH_BUY = msg["sell"][0][0]
            NOKFH_SELL = msg["buy"][0][0]
        if (msg["sell"] and msg["buy"] and msg["symbol"] == "NOKUS"):
            NOKUS_BUY = msg["sell"][0][0]
            NOKUS_SELL = msg["buy"][0][0]
        if (msg["sell"] and NOKUS_SELL != 0 and NOKFH_BUY + 10 < NOKUS_SELL):
            # Buy NOKFH, convert, sell NOKUS
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "BUY", "price" : NOKFH_BUY, "size" : msg["sell"][0][1]}
            print(json.dumps(json_string), file=exchange)
            f.write("buy NOKFH at " + str(NOKFH_BUY) + "\n")
            trade_counter += 1
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "BUY", "size" : msg["sell"][0][1]}
            print(json.dumps(json_string), file=exchange)
            trade_counter += 1
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "SELL", "price" : NOKUS_SELL, "size" : msg["sell"][0][1]}
            print(json.dumps(json_string), file=exchange)
            f.write("sell NOKUS at " + str(NOKUS_SELL) + "\n")
        elif (msg["buy"] and NOKFH_SELL != 0 and NOKUS_BUY + 10 < NOKFH_SELL):
            # Buy NOKUS, convert, sell NOKFH
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKUS", "dir" : "BUY", "price" : NOKUS_BUY, "size" : msg["sell"][0][1]}
            print(json.dumps(json_string), file=exchange)
            f.write("buy NOKUS at " + str(NOKUS_BUY) + "\n")
            trade_counter += 1
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "BUY", "size" : msg["sell"][0][1]}
            print(json.dumps(json_string), file=exchange)
            trade_counter += 1
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "NOKFH", "dir" : "SELL", "price" : NOKFH_SELL, "size" : msg["sell"][0][1]}
            print(json.dumps(json_string), file=exchange)
            f.write("sell NOKFH at " + str(NOKFH_SELL) + "\n")
    if (msg["type"] == "book" and msg["symbol"] == "BOND"):
        if (msg["sell"] and msg["sell"][0][0] < 1000 and owned_bond_shares + msg["sell"][0][1] < 100):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "BOND", "dir" : "BUY", "price" : msg["sell"][0][0], "size" : msg["sell"][0][1]}
            owned_bond_shares += msg["sell"][0][1]
            print(json.dumps(json_string), file=exchange)
            #f.write("bought " + str(trade_counter) + " " + str(msg["sell"][0][0]) + " " + str(msg["sell"][0][1]) + "\n")
            trade_counter += 1
        if (msg["buy"] and msg["buy"][0][0] > 1000 and owned_bond_shares > 0):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "BOND", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : msg["buy"][0][1]}
            owned_bond_shares -= msg["buy"][0][1]
            print(json.dumps(json_string), file=exchange)
            #f.write("sold " + str(trade_counter) + " " + str(msg["buy"][0][0]) + " " + str(msg["buy"][0][1]) + "\n")
            trade_counter += 1
    if (msg["type"] == "ack"):
        continue
        #f.write("trade " + str(msg["order_id"]) + "\n")
    print(msg, file = sys.stderr)
