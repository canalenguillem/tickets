from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ExpenseModel(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, index=True)
    amount = Column(Float)
    category = Column(String)
    date = Column(String)
    description = Column(String)
