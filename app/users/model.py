from sqlalchemy import Column, Integer, String, Float
from app.database import DATA_BASE

class User(DATA_BASE):
    __tablename__='users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    pswrd = Column(String, nullable=False)
    balance = Column(Float, default=10000.0)
    usd_balance = Column(Float, default=0.00)
    btc_balance = Column(Float, default=0.00)
    eur_balance = Column(Float, default=0.00)
    cny_balance = Column(Float, default=0.00)
