from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.crud.tickets import create_ticket, create_expense, get_expenses
from app.db.session import SessionLocal
from app.schemas.expense import Expense
from app.utils.ocr import parse_ticket_content
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-ticket/")
async def upload_ticket(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ticket_id = str(uuid.uuid4())
    content = await file.read()
    
    # Procesar la imagen con OCR
    text = parse_ticket_content(content)
    
    # Guardar el archivo y los gastos en SQLite
    create_ticket(db, ticket_id, content)
    
    expenses = parse_ticket_content(text)
    for expense in expenses:
        create_expense(db, expense, ticket_id)
    
    return {"ticket_id": ticket_id, "expenses": [expense.dict() for expense in expenses]}

@router.get("/expenses/{ticket_id}")
async def get_expenses(ticket_id: str, db: Session = Depends(get_db)):
    expenses = get_expenses(db, ticket_id)
    
    if expenses:
        return {"expenses": [expense.__dict__ for expense in expenses]}
    return {"error": "Ticket not found"}
