import pytesseract
import os

# Configura la ruta de Tesseract y el prefijo de los datos de idioma
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Ajusta la ruta según tu instalación
os.environ["TESSDATA_PREFIX"] = r"/usr/share/tesseract-ocr/5/"

print(f"TESSDATA_PREFIX is set to {os.environ['TESSDATA_PREFIX']}")

from fastapi import FastAPI, UploadFile, File
from sqlalchemy import create_engine, Column, Integer, Float, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List
import uuid
from PIL import Image
import io
import re

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ExpenseModel(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, index=True)
    amount = Column(Float)
    category = Column(String)
    date = Column(String)
    description = Column(String)

class TicketModel(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)
    file = Column(LargeBinary)

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

class Expense(BaseModel):
    amount: float
    category: str
    date: str
    description: str

def clean_text(line: str) -> str:
    # Eliminar espacios en blanco después de comas y puntos
    line = re.sub(r'\s*,\s*', ',', line)
    line = re.sub(r'\s*\.\s*', '.', line)
    # Insertar coma en los lugares apropiados si se detecta un número sin coma
    line = re.sub(r'(\d)(\s+)(\d{2})(\s*€?)$', r'\1,\3\4', line)
    return line

def parse_ticket_content(text: str) -> List[Expense]:
    expenses = []
    lines = text.split('\n')
    exclusions = ["FACTURA", "TOTAL TICKET", "DATÁFONO", "CAMBIO", "EFECTIVO", "BASE", "IVA", "IMPORTE IVA", "TOTAL"]
    
    for line in lines:
        cleaned_line = clean_text(line)
        # Detener el procesamiento si encontramos "CAMBIO" o "EFECTIVO"
        if "CAMBIO" in cleaned_line.upper() or "EFECTIVO" in cleaned_line.upper():
            break
        # Verificar si la línea contiene alguna de las descripciones a excluir
        if any(exclusion in cleaned_line.upper() for exclusion in exclusions):
            continue
        # Buscar coincidencias para descripción y precio con más precisión
        match = re.search(r"(?P<description>.+?)\s+(?P<amount>\d+[,\.]\d{2})\s*€?$", cleaned_line)
        if match:
            description = match.group("description").strip()
            amount_str = match.group("amount").replace(",", ".")
            amount = float(amount_str)
            expenses.append(Expense(
                description=description,
                amount=amount,
                category="default",  # Puedes mejorar esto clasificando según la descripción
                date="2024-06-09"    # Debes extraer la fecha real del ticket
            ))
    
    return expenses

@app.post("/upload-ticket/")
async def upload_ticket(file: UploadFile = File(...)):
    ticket_id = str(uuid.uuid4())
    content = await file.read()
    
    # Procesar la imagen con OCR
    image = Image.open(io.BytesIO(content))
    text = pytesseract.image_to_string(image, lang='spa', config='--tessdata-dir "/usr/share/tesseract-ocr/5/tessdata/"')
    print(f"text: {text}")  # Print para depuración

    # Extraer gastos del texto
    expenses = parse_ticket_content(text)
    print(f"expenses: {expenses}")  # Print para depuración
    
    # Guardar el archivo y los gastos en SQLite
    db = SessionLocal()
    ticket = TicketModel(ticket_id=ticket_id, file=content)
    db.add(ticket)
    db.commit()
    
    for expense in expenses:
        expense_record = ExpenseModel(
            ticket_id=ticket_id,
            amount=expense.amount,
            category=expense.category,
            date=expense.date,
            description=expense.description
        )
        db.add(expense_record)
    
    db.commit()
    db.close()
    
    return {"ticket_id": ticket_id, "expenses": [expense.dict() for expense in expenses]}

@app.get("/expenses/{ticket_id}")
async def get_expenses(ticket_id: str):
    db = SessionLocal()
    expenses = db.query(ExpenseModel).filter(ExpenseModel.ticket_id == ticket_id).all()
    db.close()
    
    if expenses:
        return {"expenses": [expense.__dict__ for expense in expenses]}
    return {"error": "Ticket not found"}
