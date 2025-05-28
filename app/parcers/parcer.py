
import csv
from pathlib import Path
paths = [
        r"data\BTC_USD.csv", 
        r"data\USD_RUB.csv", 
        r"data\EUR_RUB.csv", 
        r"data\CNY_RUB.csv"
]
currs=["BTC","USD","EUR","CNY"]

def get_value():
    values={c:0.0 for c in currs}
    ind=-1
    for p in paths:
        ind+=1
        with open(p, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return None
            values[currs[ind]]=float(rows[-1]["Close"])
    values["BTC"]=values["BTC"]*values["USD"]
    return values
