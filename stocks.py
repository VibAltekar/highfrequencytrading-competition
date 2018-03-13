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
    if (msg["type"] == "book" and msg["symbol"] == "GOOG"):
        if (msg["buy"]):
            if count <= 15:
                array.append(msg["buy"][0][0])
                count += 1
            if count > 15:
                array.append(msg["buy"][0][0])
                del array[0]
        if (array and count >= 15):
            GOOG_window_min = min(array)
            GOOG_window_max = max(array)
            GOOG_comp = GOOG_window_max - GOOG_threshold
            f.write("Min: " + str(GOOG_window_min) + " " + "Max: " + str(GOOG_window_max) + "\n")

        if (msg["sell"]):
            f.write(str(msg["sell"][0][0]) + "\n")
        if (count >= 15 and msg["sell"] and msg["sell"][0][0] <= GOOG_window_min and GOOG_owned + msg["sell"][0][1] < 100):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "GOOG", "dir" : "BUY", "price" : msg["sell"][0][0], "size" : msg["sell"][0][1]}
            GOOG_most_recent_min = GOOGLE_window_min
            print(json.dumps(json_string), file=exchange)
            GOOG_owned += msg["sell"][0][1]
            f.write("bought " + str(trade_counter) + " " + str(msg["sell"][0][0]) + " " + str(msg["sell"][0][1]) + "\n")
            trade_counter += 1
        if (GOOG_owned > 0 and msg["buy"] and msg["buy"][0][0] > GOOG_most_recent_min):
            json_string = {"type" : "add", "order_id" : trade_counter, "symbol" : "GOOG", "dir" : "SELL", "price" : msg["buy"][0][0], "size" : msg["buy"][0][1]}
            print(json.dumps(json_string), file=exchange)
            f.write("sold " + str(trade_counter) + " " + str(msg["buy"][0][0]) + " " + str(msg["buy"][0][1]) + "\n")
            trade_counter += 1
            GOOG_owned -= msg["buy"][0][1]
            count = 0
            array = []
    if (msg["type"] == "ack"):
        continue
        #f.write("trade " + str(msg["order_id"]) + "\n")
    print(msg, file = sys.stderr)
