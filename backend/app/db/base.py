from app.models.expense import ExpenseModel
from app.models.ticket import TicketModel
from app.db.session import engine

def init_db():
    ExpenseModel.metadata.create_all(bind=engine)
    TicketModel.metadata.create_all(bind=engine)
