from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.errors import AppError
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType


def _get_account_for_user(db: Session, user_id: int, for_update: bool = False) -> Account:
    stmt = select(Account).where(Account.user_id == user_id)
    if for_update:
        stmt = stmt.with_for_update()
    return db.execute(stmt).scalar_one()


def get_balance(db: Session, user_id: int) -> Account:
    return _get_account_for_user(db, user_id, for_update=False)


def deposit(db: Session, user_id: int, amount: float) -> Account:
    amount_d = Decimal(str(amount))
    try:
        acc = _get_account_for_user(db, user_id, for_update=True)
        acc.balance = Decimal(str(acc.balance)) + amount_d

        db.add(Transaction(account_id=acc.id, type=TransactionType.deposit, amount=amount_d))
        db.add(acc)

        db.commit()
        db.refresh(acc)
        return acc
    except Exception:
        db.rollback()
        raise


def withdraw(db: Session, user_id: int, amount: float) -> Account:
    amount_d = Decimal(str(amount))
    try:
        acc = _get_account_for_user(db, user_id, for_update=True)
        current = Decimal(str(acc.balance))
        if amount_d > current:
            raise AppError(code="insufficient_funds", message="Insufficient funds", status_code=400)

        acc.balance = current - amount_d

        db.add(Transaction(account_id=acc.id, type=TransactionType.withdraw, amount=amount_d))
        db.add(acc)

        db.commit()
        db.refresh(acc)
        return acc
    except Exception:
        db.rollback()
        raise


def transfer(
    db: Session,
    user_id: int,
    to_username: str,
    amount: float,
    comment: Optional[str] = None,
) -> None:
    amount_d = Decimal(str(amount))
    try:
        from_acc = _get_account_for_user(db, user_id, for_update=True)

        to_user = db.execute(select(User).where(User.username == to_username)).scalar_one_or_none()
        if not to_user:
            raise AppError(code="recipient_not_found", message="Recipient not found", status_code=404)
        if to_user.id == user_id:
            raise AppError(code="cannot_transfer_to_self", message="Cannot transfer to self", status_code=400)

        to_acc = _get_account_for_user(db, to_user.id, for_update=True)

        from_balance = Decimal(str(from_acc.balance))
        if amount_d > from_balance:
            raise AppError(code="insufficient_funds", message="Insufficient funds", status_code=400)

        from_acc.balance = from_balance - amount_d
        to_acc.balance = Decimal(str(to_acc.balance)) + amount_d

        db.add(Transaction(
            account_id=from_acc.id,
            type=TransactionType.transfer_out,
            amount=amount_d,
            related_account_id=to_acc.id,
            comment=comment,
        ))
        db.add(Transaction(
            account_id=to_acc.id,
            type=TransactionType.transfer_in,
            amount=amount_d,
            related_account_id=from_acc.id,
            comment=comment,
        ))

        db.add(from_acc)
        db.add(to_acc)

        db.commit()
    except Exception:
        db.rollback()
        raise
