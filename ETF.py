

BOND_PRICE = 1000
AAPL_PRICE = 1000
MSFT_PRICE = 1000
GOOG_PRICE = 1000
XLK_PRICE = 1000

def XLK_ETF(BOND_PRICE, AAPL_PRICE, MSFT_PRICE, GOOG_PRICE, XLK_PRICE):

    ADDGREGATE = 3 * BOND_PRICE + 3 * MSFT_PRICE + 2 * GOOG_PRICE + 2 * AAPL_PRICE

    DIFF = ADDGREGATE - XLK_PRICE * 10 # the price difference for one BASKET

    if DIFF > 100:
        return True
    elif DIFF < -100:
        return False
    return None