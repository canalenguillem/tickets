from pydantic import BaseModel

class UpdateExclusionsRequest(BaseModel):
    store_name: str
    new_exclusion: str
