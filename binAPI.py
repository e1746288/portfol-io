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


def report_wallet_status(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    tradeDetail = {}
    for coin in accInfo["balances"]:
        if float(coin["free"]) + float(coin["locked"]) > 0:
            try:
                orderBook = client.get_my_trades(symbol=coin["asset"]+"USDT")
                boughtWith = "USDT"
            except:
                try:
                    orderBook = client.get_my_trades(symbol=coin["asset"]+"BTC")
                    boughtWith = "BTC"
                except:
                    if coin["asset"] == "USDT":
                            orderBook = client.get_my_trades(symbol="USDTTRY")
                            boughtWith = "TRY"
                    else:
                        print("Unknown trade type for the coin: " + coin["asset"])
                        continue
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
            
            symbName = coin["asset"] + "/" + boughtWith
            tradeDetail[symbName] = {}
            tradeDetail[symbName]["avgPrice"] = totalPrice/totalQty
            tradeDetail[symbName]["qty"] = totalQty
            tradeDetail[symbName]["currentPrice"] = float(client.get_avg_price(symbol=coin["asset"]+boughtWith)["price"])
            tradeDetail[symbName]["perc"] = round(tradeDetail[symbName]["currentPrice"]/tradeDetail[symbName]["avgPrice"] - 1, 3)
    
    return tradeDetail


def report_profit(userName):
    apiKey = os.getenv('BINANCE_API_KEY_' + userName)
    apiSecret = os.getenv('BINANCE_API_SECRET_' + userName)
    client = Client(apiKey, apiSecret)
    accInfo = client.get_account()

    profitDict = {}
    for coin in accInfo["balances"]:
        if coin["asset"] != "USDT":
            try:
                orderBook = client.get_my_trades(symbol=coin["asset"]+"USDT")
                boughtWith = "USDT"
            except:
                try:
                    orderBook = client.get_my_trades(symbol=coin["asset"]+"BTC")
                    boughtWith = "BTC"
                except:
                    #print("Unknown trade type for the coin: " + coin["asset"])
                    continue
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
                    tempProfitDict["perc"] = round(float(order["price"]) / avgPrice - 1, 3)
                    if boughtWith == "BTC":
                        tempProfitDict["profit"] = profit * float(client.get_avg_price(symbol="BTCUSDT")["price"])
                    else:
                        tempProfitDict["profit"] = profit
                    profitDict[coin["asset"]].append(tempProfitDict)
                    totalQty -= float(order["qty"])
                    totalPrice = avgPrice * totalQty
            
            if profitDict[coin["asset"]] == []:
                profitDict.pop(coin["asset"])
    
    return profitDict