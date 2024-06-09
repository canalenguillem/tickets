from fastapi import FastAPI
from app.api import tickets
from app.db.base import init_db

app = FastAPI()

# Inicializar la base de datos
init_db()

# Incluir las rutas
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
