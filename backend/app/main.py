from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppError

from app.db.base import Base
from app.db.session import engine

from app.models.user import User  # noqa: F401
from app.models.account import Account  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401

from app.routers.auth import router as auth_router
from app.routers.account import router as account_router
from app.routers.transactions import router as transactions_router

app = FastAPI(title="BankSim API")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    # Приводим встроенные HTTP ошибки к единому формату
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Ошибки валидации входных данных (422)
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "Invalid request data", "details": exc.errors()}},
    )


app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transactions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
