# -*- coding: utf-8 -*-

import csv
from datetime import datetime
import binAPI

from treasury import TREASURE, MARKET

def update_treasury():
    f = open("treasury.py", "w+", encoding='utf-8')
    f.write("TREASURE = " + str(TREASURE) + "\n")
    f.write("MARKET = " + str(MARKET) + "\n")
    f.close()
    return

def backup_treasury():
    f = open("backupTreasury.py", "w+", encoding='utf-8')
    f.write("TREASURE = " + str(TREASURE) + "\n")
    f.write("MARKET = " + str(MARKET) + "\n")
    f.close()
    return

def export_portfolio(issuedBy="all"):
    csvColumns = [" "] + list(TREASURE.keys()) + ["Toplam", " ", "Alış", "Satış", "Ortalama",  " ", "Toplam TRY", "Toplam TRY (Avg)"]
    grandTotalTRY = 0
    grandTotalTRYAvg = 0
    # datetime object containing current date and time
    now = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    fileName = "portfolio-"+now+".csv"
    with open(fileName, "w", encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(csvColumns)
        
        for assetKey in list(MARKET.keys()):
            insts = list(MARKET[assetKey].keys())
            for inst in insts:
                theRow = [inst]
                total = 0
                if issuedBy == "all":
                    for person in list(TREASURE.keys()):    
                        try:
                            theRow += [TREASURE[person][assetKey][inst]]
                            total += TREASURE[person][assetKey][inst]
                        except:
                            theRow += [0]
                else:
                    try:
                        theRow += [TREASURE[issuedBy][assetKey][inst]]
                        total += TREASURE[issuedBy][assetKey][inst]
                    except:
                        theRow += [0]
                if assetKey == "coin" and inst != "USDT":
                    buyRate = MARKET[assetKey][inst]["buyRate"] * MARKET[assetKey]["USDT"]["buyRate"]
                    sellRate = MARKET[assetKey][inst]["sellRate"] * MARKET[assetKey]["USDT"]["sellRate"]
                else:
                    buyRate = MARKET[assetKey][inst]["buyRate"]
                    sellRate = MARKET[assetKey][inst]["sellRate"]
                totalTRY = total * buyRate
                avgPrice = (buyRate + sellRate) * 0.5
                grandTotalTRY += totalTRY
                totalTRYAvg = total * avgPrice
                grandTotalTRYAvg += totalTRYAvg
                theRow += [total, " ", buyRate, sellRate, avgPrice, " ", totalTRY, totalTRYAvg]
                w.writerow(theRow)
        theRow = [" "] * 9 + ["Genel Toplam:", grandTotalTRY, grandTotalTRYAvg]
        w.writerow(theRow)

def export_portfolio_alternative():
    csvColumns = [" "]
    for k in list(MARKET.keys()):
        csvColumns += list(MARKET[k].keys())
    with open("portfolio_alternative_out.csv", "w") as f:
        w = csv.writer(f)
        w.writerow(csvColumns)
        for person in list(TREASURE.keys()):
            theRow = [person]
            for assetKey in list(MARKET.keys()):
                insts = list(MARKET[assetKey].keys())
                for inst in insts:
                    try:
                        theRow += [TREASURE[person][assetKey][inst]]
                    except:
                        theRow += [0]
            w.writerow(theRow)

def report_portfolio(issuedBy="all"):
    grandTotalTRY = 0
    grandTotalTRYAvg = 0

    theRow = {}
    for assetKey in list(MARKET.keys()):
        if assetKey == "coin":
            theRow["coin"] = {}
            total = 0
            if issuedBy == "all":
                for person in list(TREASURE.keys()):
                    total += binAPI.report_wallet_TRY(person.replace("#", "_"))
            else:
                total += binAPI.report_wallet_TRY(issuedBy.replace("#", "_"))
            theRow["coin"]["TRY_value"] = total
            grandTotalTRY += total
            grandTotalTRYAvg += total
        else:
            insts = list(MARKET[assetKey].keys())
            for inst in insts:
                theRow[inst] = {}
                total = 0
                if issuedBy == "all":
                    for person in list(TREASURE.keys()):    
                        try:
                            total += TREASURE[person][assetKey][inst]
                        except:
                            total += 0
                else:
                    try:
                        total += TREASURE[issuedBy][assetKey][inst]
                    except:
                        total += 0
                buyRate = MARKET[assetKey][inst]["buyRate"]
                sellRate = MARKET[assetKey][inst]["sellRate"]
                totalTRY = total * buyRate
                avgPrice = (buyRate + sellRate) * 0.5
                grandTotalTRY += totalTRY
                totalTRYAvg = total * avgPrice
                grandTotalTRYAvg += totalTRYAvg
                theRow[inst]["Owned"] = total
                theRow[inst]["TRY_value"] = totalTRY
                theRow[inst]["TRY_value_avg"] = totalTRYAvg            
    theRow["Total"] = {}
    theRow["Total"]["net"] = grandTotalTRY
    theRow["Total"]["avg"] = grandTotalTRYAvg
    return theRow

def print_portfolio_update():
    return str(TREASURE)

def report_coin_wallet(userName, currency):
    return binAPI.report_wallet_status(userName.replace("#", "_"), currency)
    
def report_coin_profits(userName):
    return binAPI.report_profit(userName.replace("#", "_"))