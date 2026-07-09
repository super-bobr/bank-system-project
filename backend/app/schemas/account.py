from typing import Optional
from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    balance: float
    currency: str


class AmountRequest(BaseModel):
    amount: float = Field(gt=0)


class TransferRequest(BaseModel):
    to_username: str = Field(min_length=3, max_length=64)
    amount: float = Field(gt=0)
    comment: Optional[str] = Field(default=None, max_length=255)
