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

    # --- Update tracking ---
    is_active: bool = True
    updated_at: str | None = None

    # --- Creation timestamp ---
    created_at: str = datetime.utcnow().isoformat()
