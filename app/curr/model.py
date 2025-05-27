from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import DATA_BASE

class CurrencyData(DATA_BASE):
    __tablename__="curr_data"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index = True)
    value = Column(Float)
    timestamp = Column(DateTime)