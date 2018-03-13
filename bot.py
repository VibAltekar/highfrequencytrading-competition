import json
import constants
import parser

class Bot(object):
    def __init__(self):
        self.info = {}
        self.orders = {}
        self.order_id = 1
        self.holdings =  {}
        self.open = {}
        for stock in constants.SYMBOLS:
            self.positions[stock] = 0

    def process_line(self, line):
        if (line["type"] == "hello"):
            pass
        elif (line["type"] == "open"):
            self.open = parser.parse_open(line)
        elif (line["type"] == "close"):
            self.open = parser.parse_closed(line)
        elif (line["type"] == "book"):
            res = parser.parse_books(line, self.order_id)
            if res[0] == "ex":
                self.execute_order(res[1])
            elif res[0] == "info":
                self.update_info(res[1])
        elif (line["type"] == "trade"):
            pass

    def execute_order(self, order):
        # Check if came back successful, increment id_counter
        pass

    def update_info(self, details):
        pass
