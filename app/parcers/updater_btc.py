from __future__ import annotations

import argparse
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf
from pandas.errors import EmptyDataError

# ─── ПАРАМЕТРЫ CLI ─────────────────────────────────────
parser = argparse.ArgumentParser(description="BTC_USD CSV updater")
parser.add_argument("--start", type=str, help="2021-05-24")
parser.add_argument("--end",   type=str, help="2025-05-25")
args = parser.parse_args()

# ─── КОНСТАНТЫ ─────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "BTC_USD.csv"
COLS = ["Price", "Close", "High", "Low", "Open", "Volume"]


# ─── УТИЛИТЫ ───────────────────────────────────────────
def df_from_yf(data: pd.DataFrame) -> pd.DataFrame:
    """yfinance DF -> нужные колонки и порядок"""
    if data.empty:
        return pd.DataFrame(columns=COLS)
    data.reset_index(inplace=True)
    date_col = "Date" if "Date" in data else "Datetime"
    out = data[[date_col, "Close", "High", "Low", "Open", "Volume"]].copy()
    out.rename(columns={date_col: "Price"}, inplace=True)
    out["Price"] = pd.to_datetime(out["Price"], errors="coerce").dt.date.astype(str)
    return out[COLS]


def save(df: pd.DataFrame):
    df.to_csv(CSV_PATH, index=False)
    print(f"[{datetime.now(UTC):%H:%M:%S}] CSV сохранён ({len(df)} строк)")


def read_csv_safely(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except (FileNotFoundError, EmptyDataError):
        return pd.DataFrame(columns=COLS)


# ─── 1. ЕСЛИ УКАЗАН ДИАПАЗОН — ТОЛЬКО СКАЧАТЬ И ВЫЙТИ ─
if args.start:
    start_iso = args.start
    end_iso   = args.end or (datetime.now(UTC).date().isoformat())
    # yfinance `end` не включителен → смещаем на +1 день
    end_plus  = (datetime.fromisoformat(end_iso).date() + timedelta(days=1)).isoformat()

    print(f"Скачиваю BTC-USD с {start_iso} по {end_iso}…")
    data = yf.download("BTC-USD", start=start_iso, end=end_plus,
                       interval="1d", progress=False)
    new_df = df_from_yf(data)

    if new_df.empty:
        sys.exit("⚠ yfinance не вернул данных по указанному диапазону")

    csv_df = read_csv_safely(CSV_PATH)
    csv_df = pd.concat([csv_df, new_df], ignore_index=True)
    csv_df.drop_duplicates(subset="Price", keep="last", inplace=True)
    csv_df = csv_df[COLS]
    save(csv_df)
    sys.exit(0)

# ─── 2. ОБЫЧНЫЙ РЕЖИМ (live-апдейт) ───────────────────
if not CSV_PATH.exists():
    print("BTC_USD.csv не найден – скачиваю всю историю…")
    hist = yf.download("BTC-USD", period="max", interval="1d", progress=False)
    save(df_from_yf(hist))

df = read_csv_safely(CSV_PATH)
if "Date" in df.columns and "Price" not in df.columns:
    df.rename(columns={"Date": "Price"}, inplace=True)

today_iso = datetime.now(UTC).date().isoformat()
if df.empty or df["Price"].iloc[-1] != today_iso:
    print("Добавляю дневную свечу за сегодня…")
    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()
    daily = yf.download("BTC-USD", start=today_iso, end=tomorrow,
                        interval="1d", progress=False)
    df = pd.concat([df, df_from_yf(daily)], ignore_index=True)
    df.drop_duplicates(subset="Price", keep="last", inplace=True)
    df = df[COLS]
    save(df)

print("⏳ Старт live-обновления (каждые 10 с)…")
while True:
    try:
        minute = yf.download("BTC-USD", period="1d",
                             interval="1m", progress=False)
        if not minute.empty:
            df.iloc[-1] = df_from_yf(minute.tail(1)).iloc[0]
            save(df)
    except Exception as e:
        print("⚠ Ошибка live-обновления:", e)
    time.sleep(10) #300 - 5 min
