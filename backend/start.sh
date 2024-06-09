#!/bin/bash

# Activar el entorno virtual (opcional, si estás usando uno)
# source path/to/your/venv/bin/activate

# Exportar variables de entorno necesarias
export TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/"

# Iniciar la aplicación FastAPI con Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
