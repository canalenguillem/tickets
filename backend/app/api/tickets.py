from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.crud.tickets import create_ticket, create_expense, get_expenses, get_ticket_by_hash, delete_ticket_and_expenses
from app.crud.stores import get_store_by_name, get_all_stores
from app.db.session import SessionLocal
from app.schemas.expense import Expense
from app.utils.ocr import parse_ticket_content, extract_expenses, extract_store_name
from app.utils.hash import generate_file_hash
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
    
    # Generar hash del archivo
    file_hash = generate_file_hash(content)
    
    # Verificar si el hash ya existe en la base de datos
    existing_ticket = get_ticket_by_hash(db, file_hash)
    if existing_ticket:
        return {"error": "Ticket already uploaded"}
    
    # Procesar la imagen con OCR
    text = parse_ticket_content(content)
    print(f"text: {text}")  # Print para depuración
    
    # Obtener todas las tiendas conocidas
    stores = get_all_stores(db)
    known_stores = [store.name for store in stores]
    
    # Extraer el nombre de la tienda
    store_name = extract_store_name(text, known_stores)
    store = get_store_by_name(db, store_name)
    print(f"store: {store}")  # Print para depuración
    
    if not store:
        return {"error": "Store not found"}

    # Extraer gastos del texto usando las exclusiones del establecimiento
    exclusions = store.exclusions.split(',')
    expenses = extract_expenses(text, exclusions)
    print(f"expenses: {expenses}")  # Print para depuración
    
    # Guardar el archivo y los gastos en SQLite
    create_ticket(db, ticket_id, content, file_hash)
    for expense in expenses:
        create_expense(db, expense, ticket_id)
    
    return {"ticket_id": ticket_id, "store": store_name, "expenses": [expense.dict() for expense in expenses]}

@router.get("/expenses/{ticket_id}")
async def get_expenses(ticket_id: str, db: Session = Depends(get_db)):
    expenses = get_expenses(db, ticket_id)
    
    if expenses:
        return {"expenses": [expense.__dict__ for expense in expenses]}
    return {"error": "Ticket not found"}

@router.delete("/delete-ticket/{ticket_id}")
async def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = delete_ticket_and_expenses(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket and expenses deleted successfully"}
