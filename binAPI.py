# 
# https://python-binance.readthedocs.io/en/latest/overview.html
# 
import os
from dotenv import load_dotenv
from binance.client import Client
from binance.enums import *

from treasury import TREASURE

def report_wallet_USDT(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    
    person = userName.replace("_", "#")
    walletUSDT = 0
    currencyList = ["USDT", "BTC", "BNB", "TRY"]
    for coin in list(TREASURE[person]["coin"].keys()):
        totalAmount = TREASURE[person]["coin"][coin]
        if coin == "USDT":
            walletUSDT += totalAmount
            continue
        for currency in currencyList:
            try:
                avg_price = float(client.get_avg_price(symbol=coin+currency)["price"])
                if currency == "TRY":
                    walletUSDT += totalAmount * avg_price / float(client.get_avg_price(symbol="USDTTRY")["price"])
                elif currency == "USDT":
                    walletUSDT += totalAmount * avg_price
                else:
                    walletUSDT += totalAmount * avg_price * float(client.get_avg_price(symbol=currency+"USDT")["price"])
                break
            except:
                continue
    return walletUSDT

def report_wallet_TRY(userName):
    totalUSDT = report_wallet_USDT(userName)
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    avg_price = float(client.get_avg_price(symbol="USDTTRY")["price"])
    return totalUSDT * avg_price

def get_owned_coins(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    ownedCoins = {}
    for coin in accInfo["balances"]:
        if float(coin["free"]) + float(coin["locked"]) > 0:
            ownedCoins[coin["asset"]] = float(coin["free"]) + float(coin["locked"])
    return ownedCoins

def get_market_data(coinList):
    apiKey = os.getenv('BINANCE_API_KEY_DEFAULT')
    apiSecret = os.getenv('BINANCE_API_SECRET_DEFAULT')
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    coinPrices = {}
    for coin in accInfo["balances"]:
        if (float(coin["free"]) + float(coin["locked"]) > 0) or (coin["asset"] in coinList):
            if coin["asset"] == "USDT":
                    last_kline = client.get_klines(symbol=coin["asset"]+"TRY", interval=KLINE_INTERVAL_5MINUTE, limit = 1)[0]
                    coinPrices[coin["asset"]] = {}
                    coinPrices[coin["asset"]]["buyRate"] = float(last_kline[4]) #close price
                    coinPrices[coin["asset"]]["sellRate"] = float(last_kline[1]) #open price
            else:
                try:
                	last_kline = client.get_klines(symbol=coin["asset"]+"USDT", interval=KLINE_INTERVAL_5MINUTE, limit = 1)[0]
	                coinPrices[coin["asset"]] = {}
	                coinPrices[coin["asset"]]["buyRate"] = float(last_kline[4]) #close price
	                coinPrices[coin["asset"]]["sellRate"] = float(last_kline[1]) #open price
                except:
                    try:
                        last_kline = client.get_klines(symbol=coin["asset"]+"BTC", interval=KLINE_INTERVAL_5MINUTE, limit = 1)[0]
                        coinPrices[coin["asset"]] = {}
                        coinPrices[coin["asset"]]["buyRate"] = float(last_kline[4]) *  float(client.get_avg_price(symbol="BTCUSDT")["price"])#close price
                        coinPrices[coin["asset"]]["sellRate"] = float(last_kline[1]) * float(client.get_avg_price(symbol="BTCUSDT")["price"]) #open price
                    except:
                        print(coin["asset"] + " cannot be bought with USDT or BTC")
    return coinPrices

def report_wallet_status(userName, mainCurrency):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    currencyList = ["USDT", "BTC", "BNB", "TRY"]
    tradeDetail = {}
    for coin in accInfo["balances"]:
        orderBook = []
        if float(coin["free"]) + float(coin["locked"]) > 0:
            for currency in currencyList:
                try:
                    tempBook = client.get_my_trades(symbol=coin["asset"]+currency)
                except:
                    continue
                if tempBook == []:
                    continue
                if currency == "TRY":
                    for order in tempBook:
                        currencyUSDTInfo = client.get_klines(symbol=mainCurrency+currency, interval=KLINE_INTERVAL_1MINUTE, startTime=order["time"], limit = 1)[0]
                        usdtPrice = (float(currencyUSDTInfo[1]) + float(currencyUSDTInfo[4])) * 0.5
                        order["price"] = float(order["price"]) / usdtPrice                    
                elif currency != mainCurrency:
                    for order in tempBook:
                        currencyUSDTInfo = client.get_klines(symbol=currency+mainCurrency, interval=KLINE_INTERVAL_1MINUTE, startTime=order["time"], limit = 1)[0]
                        usdtPrice = (float(currencyUSDTInfo[1]) + float(currencyUSDTInfo[4])) * 0.5
                        order["price"] = float(order["price"]) * usdtPrice
                orderBook+=tempBook

            totalPrice = 0
            totalQty = 0
            avgPrice = 0
            for order in orderBook:
                if order["isBuyer"]:
                    totalPrice += float(order["price"]) * float(order["qty"])
                    totalQty += float(order["qty"])
                else:
                    avgPrice = totalPrice/totalQty
                    totalQty -= float(order["qty"])
                    totalPrice = avgPrice * totalQty
            
            if totalQty == 0:
            	continue
            
            tradeDetail[coin["asset"]] = {}
            tradeDetail[coin["asset"]]["avgPrice"] = round(totalPrice/totalQty, 5)
            tradeDetail[coin["asset"]]["qty"] = totalQty
            try:
                tradeDetail[coin["asset"]]["currentPrice"] = round(float(client.get_avg_price(symbol=coin["asset"]+"USDT")["price"]), 5)
            except:
                tradeDetail[coin["asset"]]["currentPrice"] = round(float(client.get_avg_price(symbol=coin["asset"]+"BTC")["price"]) * float(client.get_avg_price(symbol="BTCUSDT")["price"]), 5)
            tradeDetail[coin["asset"]]["perc"] = round(tradeDetail[coin["asset"]]["currentPrice"]/tradeDetail[coin["asset"]]["avgPrice"] - 1, 3)
    
    return tradeDetail


def report_profit(userName, mainCurrency):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    profitDict = {}
    currencyList = ["USDT", "BTC", "BNB", "TRY"]
    for coin in accInfo["balances"]:
        orderBook = []
        for currency in currencyList:
            try:
                tempBook = client.get_my_trades(symbol=coin["asset"]+currency)
            except:
                continue
            if tempBook == []:
                continue
            if currency == "TRY":
                for order in tempBook:
                    currencyUSDTInfo = client.get_klines(symbol=mainCurrency+currency, interval=KLINE_INTERVAL_1MINUTE, startTime=order["time"], limit = 1)[0]
                    usdtPrice = (float(currencyUSDTInfo[1]) + float(currencyUSDTInfo[4])) * 0.5
                    order["price"] = float(order["price"]) / usdtPrice                    
            elif currency != mainCurrency:
                for order in tempBook:
                    currencyUSDTInfo = client.get_klines(symbol=currency+mainCurrency, interval=KLINE_INTERVAL_1MINUTE, startTime=order["time"], limit = 1)[0]
                    usdtPrice = (float(currencyUSDTInfo[1]) + float(currencyUSDTInfo[4])) * 0.5
                    order["price"] = float(order["price"]) * usdtPrice
            orderBook+=tempBook

            totalPrice = 0
            totalQty = 0
            avgPrice = 0
            profitDict[coin["asset"]] = []

            for order in orderBook:
                if order["isBuyer"]:
                    totalPrice += float(order["price"]) * float(order["qty"])
                    totalQty += float(order["qty"])
                else:
                    tempProfitDict = {}
                    avgPrice = totalPrice/totalQty
                    profit = (float(order["price"]) - avgPrice) * float(order["qty"])
                    tempProfitDict["perc"] = round(float(order["price"]) / avgPrice - 1, 3)
                    tempProfitDict["profit"] = profit
                    profitDict[coin["asset"]].append(tempProfitDict)
                    totalQty -= float(order["qty"])
                    totalPrice = avgPrice * totalQty
            
            if profitDict[coin["asset"]] == []:
                profitDict.pop(coin["asset"])
    
    return profitDict