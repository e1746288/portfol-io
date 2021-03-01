# -*- coding: utf-8 -*-

import requests

import investmentManager as im
import fxAPI
import fundAPI
import goldAPI
import binAPI
import sharesAPI

from treasury import TREASURE, MARKET

def get_hodl_ones(entity):
    hodlList = []
    for person in list(TREASURE.keys()):
        try:
            hodlList += list(TREASURE[person][entity].keys())
        except:
            continue
    return list(set(hodlList))

def fetch_gold():
    #fetch gold prices from altınkaynak
    goldList = get_hodl_ones("gold")
    MARKET["gold"] = goldAPI.get_gold_prices(goldList)

def fetch_forex(source):
    #fetch usd/try eur/try etc. from the given source (isbank, enpara, etc.)
    fxList = get_hodl_ones("fx")
    MARKET["fx"] = fxAPI.get_fx_prices(fxList, source)

def fetch_fund():
    #fetch fund prices from TEFAS
    fundList = get_hodl_ones("fund")
    MARKET["fund"] = fundAPI.get_fund_prices(fundList)

def fetch_shares():
    #fetch fund prices from isyatirim
    sharesList = get_hodl_ones("shares")
    MARKET["shares"] = sharesAPI.get_shares_prices(sharesList)

def fetch_coin():
    #fetch coin/usdt ratio from binance
    coinList = []
    for person in list(TREASURE.keys()):
        try:
            TREASURE[person]["coin"] = binAPI.get_owned_coins(person.replace("#", "_"))
            coinList += list(TREASURE[person]["coin"].keys())
        except:
            print("Coin data is not available for the user " + person)
    coinList = list(set(coinList))
    MARKET["coin"] = binAPI.get_market_data(coinList)

def update_prices(source):
    fetch_forex(source)
    fetch_gold()
    fetch_fund()
    fetch_shares()
    fetch_coin()
    im.update_treasury()