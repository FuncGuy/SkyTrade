import telegram_send

import StockService


def getStockList():
    global stocks
    stocks = {}
    with open("watchlist.txt") as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            stocks[name.strip()] = var.strip()
    return stocks


if __name__ == "__main__":
    stocks = getStockList()
    try:
        histroical_days = 2
        interval = '5minute'
        intervalInMinutes = 1
        quantity = 1
        StockService.BuySellHistoricalStocks(histroical_days, interval, stocks, intervalInMinutes, quantity)
    except Exception as e:
        print(e)
        telegram_send.send(messages=["Error {}".format(e)])
        pass
