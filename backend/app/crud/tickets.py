from sqlalchemy.orm import Session
from app.models.ticket import TicketModel
from app.models.expense import ExpenseModel
from app.schemas.expense import Expense
from typing import List

def create_ticket(db: Session, ticket_id: str, file_content: bytes, file_hash: str):
    db_ticket = TicketModel(id=ticket_id, file=file_content, hash=file_hash)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_ticket_by_hash(db: Session, file_hash: str):
    return db.query(TicketModel).filter(TicketModel.hash == file_hash).first()

def get_expenses(db: Session, ticket_id: str) -> List[Expense]:
    return db.query(ExpenseModel).filter(ExpenseModel.ticket_id == ticket_id).all()

def create_expense(db: Session, expense: Expense, ticket_id: str):
    db_expense = ExpenseModel(**expense.dict(), ticket_id=ticket_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_ticket_and_expenses(db: Session, ticket_id: str):
    expenses = db.query(ExpenseModel).filter(ExpenseModel.ticket_id == ticket_id).all()
    for expense in expenses:
        db.delete(expense)
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
    return ticket
