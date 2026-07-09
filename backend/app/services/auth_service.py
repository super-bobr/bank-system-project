from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.errors import AppError
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.account import Account


def signup(db: Session, name: str, username: str, password: str) -> str:
    existing = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if existing:
        raise AppError(code="username_taken", message="Username already taken", status_code=409)

    user = User(name=name, username=username, password_hash=hash_password(password))
    db.add(user)
    db.flush()  # получаем user.id

    account = Account(user_id=user.id, balance=0, currency="RUB")
    db.add(account)

    db.commit()
    db.refresh(user)

    return create_access_token(subject=str(user.id))


def login(db: Session, username: str, password: str) -> str:
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if not user:
        raise AppError(code="invalid_credentials", message="Invalid credentials", status_code=401)

    if not verify_password(password, user.password_hash):
        raise AppError(code="invalid_credentials", message="Invalid credentials", status_code=401)

    if not user.is_active:
        raise AppError(code="user_inactive", message="User is inactive", status_code=403)

    return create_access_token(subject=str(user.id))
