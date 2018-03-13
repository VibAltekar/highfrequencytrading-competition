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

while (True):
    hello_from_exchange = exchange.readline().strip()
    msg = json.loads(hello_from_exchange)
    if (msg["type"] == "book" and msg["symbol"] == "BOND"):
        if (msg["sell"] and msg["sell"][0][0] < 1000 and owned_bond_shares + msg["sell"][0][1] < 100):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "BOND", "dir" : "BUY", "price" : msg["sell"][0][0], "size" : msg["sell"][0][1]}
            owned_bond_shares += msg["sell"][0][1]
            print(json.dumps(json_string), file=exchange)
            f.write("bought " + str(trade_counter) + " " + str(msg["sell"][0][0]) + " " + str(msg["sell"][0][1]) + "\n")
            trade_counter += 1
        if (msg["buy"] and msg["buy"][0][0] > 1000 and owned_bond_shares > 0):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "BOND", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : msg["buy"][0][1]}
            owned_bond_shares -= msg["buy"][0][1]
            print(json.dumps(json_string), file=exchange)
            f.write("sold " + str(trade_counter) + " " + str(msg["buy"][0][0]) + " " + str(msg["buy"][0][1]) + "\n")
            trade_counter += 1
    if (msg["type"] == "ack"):
        f.write("trade " + str(msg["order_id"]) + "\n")
    print(msg, file = sys.stderr)
