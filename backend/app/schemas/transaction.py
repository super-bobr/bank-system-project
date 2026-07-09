from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    related_account_id: Optional[int]
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
