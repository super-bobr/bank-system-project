from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.session import get_db
from app.routers.deps import get_current_user
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionResponse])
def list_transactions(limit: int = 5, db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = db.execute(select(Account).where(Account.user_id == user.id)).scalar_one()

    stmt = (
        select(Transaction)
        .where(Transaction.account_id == account.id)
        .order_by(desc(Transaction.created_at), desc(Transaction.id))
        .limit(min(limit, 100))
    )
    return db.execute(stmt).scalars().all()
