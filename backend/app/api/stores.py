from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.stores import create_store, get_store_by_name, update_store_exclusions
from app.db.session import SessionLocal
from app.schemas.store import Store
from app.schemas.update_exclusions import UpdateExclusionsRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/stores/")
async def create_new_store(store: Store, db: Session = Depends(get_db)):
    db_store = get_store_by_name(db, store.name)
    if db_store:
        return {"error": "Store already exists"}
    return create_store(db, store)

@router.post("/stores/update-exclusions/")
async def update_exclusions(request: UpdateExclusionsRequest, db: Session = Depends(get_db)):
    stores = update_store_exclusions(db, request.store_name, request.new_exclusion)
    if not stores:
        return {"error": "No stores found"}
    return {"message": "Exclusions updated successfully", "stores": [store.name for store in stores]}
