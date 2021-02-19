# 
# https://python-binance.readthedocs.io/en/latest/overview.html
# 
import os
from dotenv import load_dotenv
from binance.client import Client
from binance.enums import *

def report_wallet_USDT(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    # Get wallet info
    walletUSDT = 0
    for coin in accInfo["balances"]:
        if coin["asset"] != "USDT":
            totalAmount = float(coin["free"]) + float(coin["locked"])
            avg_price = float(client.get_avg_price(symbol=coin["asset"]+"USDT")["price"])
            walletUSDT += totalAmount * avg_price
        elif coin["asset"] == "USDT":
            walletUSDT += float(coin["free"]) + float(coin["locked"])
        else:
            print(coin["asset"] + " could not be bought with USDT or BTC")
    return walletUSDT


def report_wallet_TRY(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)

    totalUSDT = report_wallet_USDT(userName)
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
            try:
                last_kline = client.get_klines(symbol=coin["asset"]+"USDT", interval=KLINE_INTERVAL_5MINUTE, limit = 1)[0]
                coinPrices[coin["asset"]] = {}
                coinPrices[coin["asset"]]["buyRate"] = float(last_kline[4]) #close price
                coinPrices[coin["asset"]]["sellRate"] = float(last_kline[1]) #open price
            except:
                if coin["asset"] == "USDT":
                    last_kline = client.get_klines(symbol=coin["asset"]+"TRY", interval=KLINE_INTERVAL_5MINUTE, limit = 1)[0]
                    coinPrices[coin["asset"]] = {}
                    coinPrices[coin["asset"]]["buyRate"] = float(last_kline[4]) #close price
                    coinPrices[coin["asset"]]["sellRate"] = float(last_kline[1]) #open price
                else:
                    print(coin["asset"] + " cannot be bought with USDT")
    return coinPrices


def report_profit(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    tradeDetail = {}
    profitDict = {}
    for coin in accInfo["balances"]:
        if coin["asset"] != "USDT":
            try:
                orderBook = client.get_my_trades(symbol=coin["asset"]+"USDT")
            except:
                try:
                    orderBook = client.get_my_trades(symbol=coin["asset"]+"BTC")
                except:
                    print("Unknown trade type")
            totalPrice = 0
            totalQty = 0
            avgPrice = 0
            profitDict[coin["asset"]] = []
            for order in orderBook:
                if order["isBuyer"]:
                    totalPrice += float(order["price"]) * float(order["qty"])
                    totalQty += float(order["qty"])
                else:
                    avgPrice = totalPrice/totalQty
                    tempProfitDict = {}
                    profit = (float(order["price"]) - avgPrice) * float(order["qty"])
                    tempProfitDict["perc"] = float(order["price"]) / avgPrice
                    tempProfitDict["profit"] = profit
                    profitDict[coin["asset"]].append(tempProfitDict)
                    totalQty -= float(order["qty"])
                    totalPrice = avgPrice * totalQty
            
            if profitDict[coin["asset"]] == []:
                profitDict.pop(coin["asset"])
            
            if float(coin["free"]) + float(coin["locked"]) > 0:
                tradeDetail[coin["asset"]] = {}
                tradeDetail[coin["asset"]]["avgPrice"] = totalPrice/totalQty
                tradeDetail[coin["asset"]]["qty"] = totalQty
                tradeDetail[coin["asset"]]["currentPrice"] = float(client.get_avg_price(symbol=coin["asset"]+"USDT")["price"])
                tradeDetail[coin["asset"]]["perc"] = round(tradeDetail[coin["asset"]]["currentPrice"]/tradeDetail[coin["asset"]]["avgPrice"] - 1, 3)
    
    return tradeDetail, profitDict