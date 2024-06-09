import pytesseract
import re
import os
from PIL import Image
import io
from typing import List
from app.schemas.expense import Expense
from fuzzywuzzy import fuzz

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
os.environ["TESSDATA_PREFIX"] = r'/usr/share/tesseract-ocr/5/'

def clean_text(line: str) -> str:
    line = re.sub(r'\s*,\s*', ',', line)
    line = re.sub(r'\s*\.\s*', '.', line)
    line = re.sub(r'(\d)(\s+)(\d{2})(\s*€?)$', r'\1,\3\4', line)
    return line

def parse_ticket_content(content: bytes) -> str:
    image = Image.open(io.BytesIO(content))
    text = pytesseract.image_to_string(image, lang='spa', config='--tessdata-dir "/usr/share/tesseract-ocr/5/tessdata/"')
    return text

def extract_store_name(text: str, known_stores: List[str]) -> str:
    lines = text.split('\n')
    for line in lines:
        for store in known_stores:
            if store.lower() in line.lower():
                return store
    return 'Unknown'

def is_similar(text: str, keywords: List[str], threshold: int = 80) -> bool:
    for keyword in keywords:
        if fuzz.partial_ratio(text.lower(), keyword.lower()) > threshold:
            return True
    return False

def extract_expenses(text: str, exclusions: List[str]) -> List[Expense]:
    expenses = []
    lines = text.split('\n')
    temp_description = None
    
    i = 0
    while i < len(lines):
        cleaned_line = clean_text(lines[i])
        if is_similar(cleaned_line, exclusions):
            temp_description = None
            i += 1
            continue
        
        # Buscar coincidencias para descripción y precio con más precisión
        match = re.search(r'(?P<description>.+?)\s+(?P<amount>\d+[.,]?\d{0,2})$', cleaned_line)
        if match:
            description = match.group('description').strip()
            amount_str = match.group('amount').replace(',', '.')
            try:
                amount = float(amount_str)
                expenses.append(Expense(
                    description=description,
                    amount=amount,
                    category='default',
                    date='2024-06-09'
                ))
                temp_description = None
                i += 1
                continue
            except ValueError:
                temp_description = None
                i += 1
                continue
        
        # Si la línea actual no contiene un precio, guardar la descripción temporalmente
        temp_description = cleaned_line.strip()
        
        # Revisar la siguiente línea si contiene cantidad y precio
        if i + 1 < len(lines):
            next_line = clean_text(lines[i + 1])
            print(f'temp_description: {temp_description}')
            print(f'next_line: {next_line}')
            parts = next_line.split(')')
            if len(parts) == 2:
                unit_price_str = parts[0].split(' ')[1].strip().replace(',', '.')
                total_amount_str = parts[1].strip().replace(',', '.')
                try:
                    unit_price = float(unit_price_str)
                    total_amount = float(total_amount_str)
                    quantity = total_amount / unit_price
                    if quantity.is_integer():
                        expenses.append(Expense(
                            description=f'{temp_description} (x{int(quantity)} @ {unit_price:.2f} €)',
                            amount=total_amount,
                            category='default',
                            date='2024-06-09'
                        ))
                        # Saltar la siguiente línea ya que ya ha sido procesada
                        temp_description = None
                        i += 2
                        continue
                except ValueError:
                    temp_description = None
                    i += 1
                    continue

        i += 1

    return expenses
