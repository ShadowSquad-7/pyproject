import yfinance as yf
import pandas as pd

# Определяем тикеры для каждой валютной пары
tickers = {
    'BTC-USD': 'BTC-USD',
    'USD-RUB': 'USDRUB=X',
    'EUR-RUB': 'EURRUB=X',
     # Используем тикер для юаня к доллару
}

# Определяем период для загрузки данных
start_date = '2024-04-14'
end_date = '2025-04-14'

# Загружаем данные и сохраняем их в CSV файлы
data_frames = {}
for name, ticker in tickers.items():
    data = yf.download(ticker, start=start_date, end=end_date)
    file_name = f"{name.replace('-', '_')}.csv"
    data.to_csv(file_name)
    print(f"Data for {name} saved to {file_name}")
    data_frames[name] = data

#


