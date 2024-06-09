import pytesseract
import re
from PIL import Image
import io
from typing import List
from app.schemas.expense import Expense

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
os.environ["TESSDATA_PREFIX"] = r"/usr/share/tesseract-ocr/5/"

def clean_text(line: str) -> str:
    line = re.sub(r'\s*,\s*', ',', line)
    line = re.sub(r'\s*\.\s*', '.', line)
    line = re.sub(r'(\d)(\s+)(\d{2})(\s*€?)$', r'\1,\3\4', line)
    return line

def parse_ticket_content(content: bytes) -> str:
    image = Image.open(io.BytesIO(content))
    text = pytesseract.image_to_string(image, lang='spa', config='--tessdata-dir "/usr/share/tesseract-ocr/5/tessdata/"')
    return text

def extract_expenses(text: str) -> List[Expense]:
    expenses = []
    lines = text.split('\n')
    exclusions = ["FACTURA", "TOTAL TICKET", "DATÁFONO", "CAMBIO", "EFECTIVO", "BASE", "IVA", "IMPORTE IVA", "TOTAL"]
    
    for line in lines:
        cleaned_line = clean_text(line)
        if "CAMBIO" in cleaned_line.upper() or "EFECTIVO" in cleaned_line.upper():
            break
        if any(exclusion in cleaned_line.upper() for exclusion in exclusions):
            continue
        match = re.search(r"(?P<description>.+?)\s+(?P<amount>\d+[,\.]\d{2})\s*€?$", cleaned_line)
        if match:
            description = match.group("description").strip()
            amount_str = match.group("amount").replace(",", ".")
            amount = float(amount_str)
            expenses.append(Expense(
                description=description,
                amount=amount,
                category="default",
                date="2024-06-09"
            ))
    
    return expenses
