from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.deps import get_current_user
from app.schemas.user import UserResponse
from app.schemas.account import BalanceResponse, AmountRequest, TransferRequest
from app.services import banking_service

router = APIRouter(tags=["account"])


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user


@router.get("/account/balance", response_model=BalanceResponse)
def balance(db: Session = Depends(get_db), user=Depends(get_current_user)):
    acc = banking_service.get_balance(db, user.id)
    return BalanceResponse(balance=float(acc.balance), currency=acc.currency)


@router.post("/account/deposit", response_model=BalanceResponse)
def deposit(payload: AmountRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    acc = banking_service.deposit(db, user.id, payload.amount)
    return BalanceResponse(balance=float(acc.balance), currency=acc.currency)


@router.post("/account/withdraw", response_model=BalanceResponse)
def withdraw(payload: AmountRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    acc = banking_service.withdraw(db, user.id, payload.amount)
    return BalanceResponse(balance=float(acc.balance), currency=acc.currency)


@router.post("/account/transfer")
def transfer(payload: TransferRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    banking_service.transfer(db, user.id, payload.to_username, payload.amount, payload.comment)
    return {"status": "ok"}
