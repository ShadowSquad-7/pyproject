import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(exist_ok=True)

TICKERS = {
    'BTC_USD': 'BTC-USD',
    'USD_RUB': 'USDRUB=X',
    'EUR_RUB': 'EURRUB=X',
    'CNY_USD': 'CNYUSD=X',
}

TODAY = datetime.today().strftime('%Y-%m-%d')
START_DATE = '2024-04-14'
END_DATE = TODAY
COLUMNS = ["Price", "Close", "High", "Low", "Open", "Volume"]

data_frames = {}

for name, ticker in TICKERS.items():
    df = yf.download(ticker, start=START_DATE, end=END_DATE)

    if df.empty:
        print(f"‼ Пропущено: {name} (пустые данные)")
        continue

    df = df.rename_axis("Price").reset_index()
    df["Volume"] = df["Volume"] if "Volume" in df.columns else 0
    df = df[["Price", "Close", "High", "Low", "Open", "Volume"]]

    out_path = DATA_DIR / f"{name}.csv"
    df.to_csv(out_path, index=False)
    data_frames[name] = df.set_index("Price")

if "CNY_USD" in data_frames and "USD_RUB" in data_frames:
    cny = data_frames["CNY_USD"]
    usd = data_frames["USD_RUB"]

    common_dates = cny.index.intersection(usd.index)

    cnyrub = pd.DataFrame(index=common_dates)
    for col in ["Close", "High", "Low", "Open"]:
        cnyrub[col] = cny.loc[common_dates, col].values * usd.loc[common_dates, col].values
    cnyrub["Volume"] = 0

    cnyrub = cnyrub.reset_index()[["Price", "Close", "High", "Low", "Open", "Volume"]]
    out_file = DATA_DIR / "CNY_RUB.csv"
    cnyrub.to_csv(out_file, index=False)
else:
    print("‼ Отсутствуют данные для CNY_USD или USD_RUB — не создан CNY_RUB")