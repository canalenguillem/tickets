from sqlalchemy.orm import Session
from app.models.ticket import TicketModel
from app.models.expense import ExpenseModel
from app.schemas.expense import Expense

def create_ticket(db: Session, ticket_id: str, file: bytes):
    ticket = TicketModel(ticket_id=ticket_id, file=file)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def create_expense(db: Session, expense: Expense, ticket_id: str):
    expense_record = ExpenseModel(
        ticket_id=ticket_id,
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        description=expense.description
    )
    db.add(expense_record)
    db.commit()
    db.refresh(expense_record)
    return expense_record

def get_expenses(db: Session, ticket_id: str):
    return db.query(ExpenseModel).filter(ExpenseModel.ticket_id == ticket_id).all()
