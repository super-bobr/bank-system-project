from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import SignUpRequest, TokenResponse
from app.services.auth_service import signup, login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignUpRequest, db: Session = Depends(get_db)):
    token = signup(db, payload.name, payload.username, payload.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login_route(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = login(db, form.username, form.password)
    return TokenResponse(access_token=token)
