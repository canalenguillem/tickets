from sqlalchemy.orm import Session
from app.models.store import StoreModel
from app.schemas.store import Store
from typing import List

def get_store_by_name(db: Session, name: str):
    return db.query(StoreModel).filter(StoreModel.name == name).first()

def get_all_stores(db: Session):
    return db.query(StoreModel).all()

def create_store(db: Session, store: Store):
    db_store = StoreModel(name=store.name, exclusions=store.exclusions)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

def update_store_exclusions(db: Session, store_name: str, new_exclusion: str):
    stores = []
    if store_name:
        store = get_store_by_name(db, store_name)
        if store:
            stores.append(store)
    else:
        stores = get_all_stores(db)
    
    for store in stores:
        exclusions = set(store.exclusions.split(','))
        exclusions.add(new_exclusion)
        store.exclusions = ','.join(exclusions)
        db.commit()
    return stores
