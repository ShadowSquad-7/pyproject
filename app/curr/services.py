from app.database import asession_generator
from app.parcers.yfinance_parcer import fetch_curr_value
from app.curr.model import CurrencyData

from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio

SYMBOLS = {
    "BTC": "BTC-USD",
    'USD': "USDRUB=X",
    'EUR': "EURRUB=X",
    'CNY': "CNYRUB=X"
}

async def fetch_and_store():
    async with asession_generator() as session:
        for name, symbol in SYMBOLS.items():
            value, timestamp = fetch_curr_value(symbol)
            if value:
                session.add(CurrencyData(currency=name, value=value, timestamp=timestamp))
        await session.commit()

async def start_background_fetch():
    while True:
        await fetch_and_store()
        await asyncio.sleep(300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_background_fetch())
    yield
    task.cancel()
