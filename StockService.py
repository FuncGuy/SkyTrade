from datetime import datetime, timedelta

import talib
import pandas as pd
import telegram_send
from kiteconnect import KiteConnect


def BuySellHistoricalStocks(fetch_histroical_days, interval, stocks, intervalInMinutes, quantity):
    api_key = open('api_key.txt', 'r').read()
    api_secret = open('api_secret.txt', 'r').read()
    # if I already have access tickerCode , then following steps are required
    access_token = open('access_token.txt', 'r').read()
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    # Below method has to execute 1 time only when the script is executed for the first time

    #getAccessTokenFirstTime(api_secret, kite)

    # Dates in between which you want to fetch historical data

    from_date = datetime.strftime(datetime.now() - timedelta(fetch_histroical_days), '%Y-%m-%d')
    to_date = datetime.today().strftime('%Y-%m-%d')
    while True:
        print("\U0001F4C8", "Fetching historical data from {} to {}".format(to_date, from_date))
        # Fetch the historical data only at the end of 5 minutes
        # current second must be 0 and current minute must be fully divisible by 5 -> remainder should be 0
        if (datetime.now().second == 0) and (datetime.now().minute % intervalInMinutes == 0):
            for tickerCode in stocks:
                telegram_send.send(messages=["fetching data for {}".format(stocks[tickerCode])])
                records = kite.historical_data(tickerCode, from_date=from_date, to_date=to_date, interval=interval)
                print(records)
                df = pd.DataFrame(records)
                print(df)
                df.drop(df.tail(1).index, inplace=True)

                telegram_send.send(messages=["BKT records {}".format(records)])

                # open = df['open'].values
                high = df['high'].values
                low = df['low'].values
                close = df['close'].values
                volume = df['volume'].values

                # Calculate SMA
                sma5 = talib.SMA(close, 5)
                sma20 = talib.SMA(close, 20)

                print(sma5[-1])
                print(sma20[-1])

                price = kite.ltp('NSE:' + stocks[tickerCode])
                ltp = price['NSE:' + stocks[tickerCode]]['last_price']

                buyShare(kite, ltp, sma20, sma5, tickerCode, stocks, quantity)

                sellShare(kite, ltp, sma20, sma5, tickerCode, stocks, quantity)


def getAccessTokenFirstTime(api_secret, kite):
    print(kite.login_url())
    data = kite.generate_session("3sh60j0XlVTNGTW1MEaKPjsyf41nioVb", api_secret=api_secret)
    kite.set_access_token(data['access_token'])
    with open('access_token.txt', 'w') as ak:
        ak.write(data['access_token'])


def sellShare(kite, ltp, sma20, sma5, token, tokens, quantity):
    if (sma5[-2] > sma20[-2]) and (sma5[-1] < sma20[-1]):
        print("Sell")
        telegram_send.send(messages=["Selling Share at {}".format(ltp)])
        sell_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                         exchange=kite.EXCHANGE_NSE,
                                         order_type=kite.ORDER_TYPE_MARKET,
                                         tradingsymbol=tokens[token],
                                         transaction_type=kite.TRANSACTION_TYPE_SELL,
                                         quantity=quantity,
                                         validity=kite.VALIDITY_DAY,
                                         product=kite.PRODUCT_MIS)
        print(kite.orders())


def buyShare(kite, ltp, sma20, sma5, token, tokens, quantity):
    if (sma5[-2] < sma20[-2]) and (sma5[-1] > sma20[-1]):
        print("Buy")
        telegram_send.send(messages=["Bought the Share at {}".format(ltp)])
        buy_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NSE,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        tradingsymbol=tokens[token],
                                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        quantity=quantity,
                                        validity=kite.VALIDITY_DAY,
                                        product=kite.PRODUCT_MIS)
        print(kite.orders())
