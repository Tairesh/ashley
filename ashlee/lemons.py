from time import time
import math

import requests

YAHOO_API = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{}?modules=price"
DOGE_USD = "DOGE-USD"
RUB_USD = "RUB=X"

cache = {
    'doge_price': 4.5,
    'updated_at': 0.0,
}


def get_price(count: int) -> int:
    """
    Calculates lemon price
    :param count: Lemons capitalisation
    :return:
    """
    if time() - cache['updated_at'] > 10*60:
        doge_data = requests.get(YAHOO_API.format(DOGE_USD)).json()
        doge_price = doge_data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
        rub_data = requests.get(YAHOO_API.format(RUB_USD)).json()
        rub_price = rub_data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
        cache['doge_price'] = doge_price * rub_price
        cache['updated_at'] = time()
    k = math.log2(count) + 14.88
    price = round(cache['doge_price'] * k)
    if price < 100:
        price = 100
    return price
