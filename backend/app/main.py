from fastapi import FastAPI
from app.api import tickets, stores
from app.db.base import init_db

app = FastAPI()

# Inicializar la base de datos
init_db()

# Incluir las rutas
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(stores.router, prefix="/api/stores", tags=["stores"])
