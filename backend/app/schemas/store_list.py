from pydantic import BaseModel
from typing import List

class StoreBase(BaseModel):
    name: str
    exclusions: str

class StoreList(BaseModel):
    stores: List[StoreBase]
