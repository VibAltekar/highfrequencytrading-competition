import json
import constants

def parse_open(msg):
    return msg["symbols"]

def parse_closed(msg):
    res = []
    for stock in constants.SYMBOLS:
        if stock not in msg["symbols"]:
            res += [stock]
    return res

def parse_books(msg, order_id):
    if (msg["symbol"] == "BOND"):
        parse_bond(msg["buy"], msg["sell"], order_id)

def parse_bond(buy, sell, order_id, selling):
    # Bond fair price is 1000
    if (selling and sell and sell[0][0] <= 1000):
        # Buy bond shares
        return ("ex", {"type": "add", "order_id": order_id, "symbol": "BOND", "dir": "BUY", "price": sell[0][0], "size": sell[0][1]})
    else:
        if (buy):
            return ("info", {"price" : buy[0][0], "size" : buy[0][1]})


if __name__ == "__main__":
    pass
