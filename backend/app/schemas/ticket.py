from pydantic import BaseModel

class Ticket(BaseModel):
    ticket_id: str

    class Config:
        orm_mode = True
