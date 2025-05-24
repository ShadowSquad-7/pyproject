import io
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ───────────────────────────────
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(exist_ok=True)
COLUMNS = ['Price', 'Close', 'High', 'Low', 'Open', 'Volume']
TODAY = datetime.today().strftime('%Y-%m-%d')
TOMORROW = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')


def load_csv(path):
    """Загрузить CSV или создать новый."""
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=COLUMNS)


def append_rows(df, new_rows):
    """Добавить строки, если их нет."""
    for row in new_rows:
        if row['Price'] not in df['Price'].values:
            df = df._append(row, ignore_index=True)
        else:
            df.loc[df['Price'] == row['Price']] = list(row.values())
    return df


def download_rows(ticker):
    """Скачать дневные свечи (за сегодня), вернуть list[dict]."""
    raw = yf.download(start=TODAY, end=TOMORROW, tickers=ticker)
    csv = pd.read_csv(io.StringIO(raw.to_csv(index=True)), header=None, skiprows=2)

    rows = []
    for i in range(1, len(csv)):
        r = csv.iloc[i]
        rows.append({
            'Price': r[0],
            'Close': float(r[1]),
            'High': float(r[2]),
            'Low': float(r[3]),
            'Open': float(r[4]),
            'Volume': int(r[5]) if not pd.isna(r[5]) else 0
        })
    return rows


def update_usd():
    path = DATA_DIR / "USD_RUB.csv"
    df = load_csv(path)
    rows = download_rows("USDRUB=X")
    df = append_rows(df, rows)
    df.to_csv(path, index=False)
    print("[USD] Обновлено:", df.iloc[-1]['Price'])


def update_eur():
    path = DATA_DIR / "EUR_RUB.csv"
    df = load_csv(path)
    rows = download_rows("EURRUB=X")
    df = append_rows(df, rows)
    df.to_csv(path, index=False)
    print("[EUR] Обновлено:", df.iloc[-1]['Price'])


def update_cny():
    path = DATA_DIR / "CNY_RUB.csv"
    df = load_csv(path)

    # Получаем CNY→USD и USD→RUB
    cnyusd = yf.download("CNYUSD=X", start=TODAY, end=TOMORROW)
    usdrub = yf.download("USDRUB=X", start=TODAY, end=TOMORROW)

    if cnyusd.empty or usdrub.empty:
        print("‼ Ошибка при получении данных CNY или USD")
        return

    c = cnyusd.iloc[-1]
    u = usdrub.iloc[-1]

    price = datetime.today().strftime('%Y-%m-%d')

    cnyrub_row = {
        'Price': price,
        'Close': float(c['Close']) * float(u['Close']),
        'High':  float(c['High'])  * float(u['High']),
        'Low':   float(c['Low'])   * float(u['Low']),
        'Open':  float(c['Open'])  * float(u['Open']),
        'Volume': 0
    }

    df = append_rows(df, [cnyrub_row])
    df.to_csv(path, index=False)
    print("[CNY] Обновлено:", cnyrub_row['Price'])


# ───────────────────────────────
if __name__ == "__main__":
    print("▶ Обновление курсов USD, EUR, CNY → RUB каждые 5 минут")

    while True:
        try:
            update_usd()
            update_eur()
            update_cny()
        except Exception as e:
            print("‼ Ошибка:", e)
        time.sleep(10)  # 5 минут
