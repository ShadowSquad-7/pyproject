from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.curr.model import CurrencyData
from app.database import asession_generator
from app.users.security import get_db

router = APIRouter()


@router.get("/api/currency-data")
async def get_currency_data(
    db: Annotated[AsyncSession, Depends(get_db)],
    currency: str = Query(..., example="BTC"),
    period: str = Query("day", enum=["hour", "day", "month", "year"]),
):
    now = datetime.now()

    if period == "hour":
        start_time = now - timedelta(hours=1)
    elif period == "day":
        start_time = now - timedelta(days=1)
    elif period == "month":
        start_time = now - timedelta(days=30)
    elif period == "year":
        start_time = now - timedelta(days=365)

    query = (
        select(CurrencyData)
        .where(CurrencyData.currency == currency.upper())
        .where(CurrencyData.timestamp >= start_time)
        .order_by(CurrencyData.timestamp)
    )
    result = await db.execute(query)
    rows = result.scalars().all()

    return {
        "currency": currency,
        "period": period,
        "data": [
            {"timestamp": row.timestamp.isoformat(), "value": row.value}
            for row in rows
        ]
    }
