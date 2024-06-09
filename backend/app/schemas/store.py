from pydantic import BaseModel

class Store(BaseModel):
    name: str
    exclusions: str

    class Config:
        from_attributes = True
