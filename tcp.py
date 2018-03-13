import sys
import socket
import json
import bot

def connect(serv_addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serv_addr, int(port)))
    return (s, s.makefile('rw', 1))

bot = bot.Bot()

s, exchange = connect("test-exch-KPCBTRAPHOUSE",25000)
json_string = '{"type": "hello", "team":"KPCBTRAPHOUSE"}'
print(json_string, file=exchange)

<<<<<<< Updated upstream
while True:
    hello_from_exchange = exchange.readline().strip()
    print("The exchange replied: %s" % str(hello_from_exchange),file = sys.stderr)
=======
while (True):
    hello_from_exchange = exchange.readline().strip()
    msg = json.loads(hello_from_exchange)
    #bot.process_line(msg)
    print(msg, file = sys.stderr)
>>>>>>> Stashed changes
