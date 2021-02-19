import requests
import datetime
import time

sourceParams = {
    "isbank":
        {
            "url": "https://www.isbank.com.tr/_vti_bin/DV.Isbank/PriceAndRate/PriceAndRateService.svc/GetFxRates",
            "params": 
                {
                    "Lang":"tr",
                    "fxRateType":"IB",
                    "date":datetime.datetime.now().date().__str__(),
                    "time" : int(time.time()*1000)
                }
        }
}

def get_fx_prices(fxList, source):
    fxDict = {}
    fxDict["try"] = {}
    fxDict["try"]["buyRate"] = 1.0
    fxDict["try"]["sellRate"] = 1.0

    resp = requests.get(sourceParams[source]["url"], params = sourceParams[source]["params"])
    data = resp.json()
    if resp.ok and data["Success"]:
        for e in data["Data"]:
            fxCode = e["code"].lower()
            if fxCode in fxList:
                fxDict[fxCode] = {}
                fxDict[fxCode]["buyRate"] = e["fxRateBuy"]
                fxDict[fxCode]["sellRate"] = e["fxRateSell"]
    return fxDict