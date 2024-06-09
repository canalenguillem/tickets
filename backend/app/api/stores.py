from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.stores import create_store, get_store_by_name, get_all_stores, update_store_exclusions, create_multiple_stores
from app.db.session import SessionLocal
from app.schemas.store import Store
from app.schemas.store_list import StoreList, StoreBase
from app.schemas.update_exclusions import UpdateExclusionsRequest
from typing import List  # Asegúrate de importar List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
async def create_new_store(store: Store, db: Session = Depends(get_db)):
    db_store = get_store_by_name(db, store.name)
    if db_store:
        return {"error": "Store already exists"}
    return create_store(db, store)

@router.post("/update-exclusions/")
async def update_exclusions(request: UpdateExclusionsRequest, db: Session = Depends(get_db)):
    stores = update_store_exclusions(db, request.store_name, request.new_exclusion)
    if not stores:
        return {"error": "No stores found"}
    return {"message": "Exclusions updated successfully", "stores": [store.name for store in stores]}

@router.get("/")
async def get_stores(db: Session = Depends(get_db)):
    stores = get_all_stores(db)
    return [{"name": store.name, "exclusions": store.exclusions} for store in stores]

@router.post("/create-multiple/")
async def create_multiple_stores_endpoint(store_list: List[StoreBase], db: Session = Depends(get_db)):
    created_stores = create_multiple_stores(db, store_list)
    return [{"name": store.name, "exclusions": store.exclusions} for store in created_stores]
