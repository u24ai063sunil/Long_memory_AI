from pydantic import BaseModel
from datetime import datetime

class Memory(BaseModel):
    session_id: str
    type: str
    key: str
    value: str
    confidence: float
    source_turn: int
    last_used_turn: int
    created_at: datetime = datetime.utcnow()
