import enum
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, DateTime, func, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TransactionType(str, enum.Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    transfer_in = "transfer_in"
    transfer_out = "transfer_out"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)

    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType, name="transaction_type"))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))

    related_account_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="transactions")