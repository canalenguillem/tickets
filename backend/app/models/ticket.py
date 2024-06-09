from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TicketModel(Base):
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True, index=True)
    file = Column(LargeBinary, nullable=False)
    hash = Column(String, unique=True, nullable=False)  # Añadir columna hash