from sqlalchemy import Column, Integer, String
from app.database import DATA_BASE

class User(DATA_BASE):
    __tablename__='users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    pswrd = Column(String, nullable=False)
