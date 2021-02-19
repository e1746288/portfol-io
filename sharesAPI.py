import requests

sourceParams = {
    "isyatirim":
        {
            "url": "https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/OneEndeks",
            "params": 
                {
                    "endeks": ""
                }
        }
}

def get_shares_prices(sharesList, source = "isyatirim"):
    sharesDict = {}

    for share in sharesList:
        sourceParams[source]["params"]["endeks"] = share + ".E.BIST"
        resp = requests.get(sourceParams[source]["url"], params = sourceParams[source]["params"])
        data = resp.json()
        if resp.ok and data["Success"]:
            sharesDict[share] = {}
            sharesDict[share]["buyRate"] = data[0]['last']
            sharesDict[share]["sellRate"] = data[0]['last']
    return sharesDict
