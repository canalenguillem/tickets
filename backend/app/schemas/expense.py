from pydantic import BaseModel

class Expense(BaseModel):
    amount: float
    category: str
    date: str
    description: str

    class Config:
        orm_mode = True
