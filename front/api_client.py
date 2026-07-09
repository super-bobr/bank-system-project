"""Тонкий HTTP-клиент к API друга (FastAPI).

Все функции здесь просто вызывают эндпоинты и возвращают распарсенный JSON.
Ошибки сервера (формат {"error": {"code": ..., "message": ...}}) превращаются
в понятные исключения из exceptions.py — остальной код (auth.py, commands/*)
ловит уже только BankError и его подклассы, ему не нужно знать про HTTP.
"""

import requests

from config import API_BASE_URL
from exceptions import (
    BankError,
    ValidationError,
    InvalidCredentials,
    DuplicateUserError,
    UserNotFound,
    InsufficientFunds,
    SessionExpired,
    SelfTransferError,
    UserInactive,
)

# Соответствие кодов ошибок API друга (app/core/errors.py, AppError.code)
# нашим локальным исключениям.
ERROR_MAP = {
    "username_taken": DuplicateUserError,
    "invalid_credentials": InvalidCredentials,
    "insufficient_funds": InsufficientFunds,
    "recipient_not_found": UserNotFound,
    "cannot_transfer_to_self": SelfTransferError,
    "user_inactive": UserInactive,
    "validation_error": ValidationError,
}

# Сервер друга присылает message на английском ("Insufficient funds" и т.д.) —
# подменяем на понятные русские формулировки. Если код неизвестен, используем
# то, что прислал сервер (лучше так, чем ничего).
RU_MESSAGES = {
    "username_taken": "Пользователь с таким логином уже существует",
    "invalid_credentials": "Неверный логин или пароль",
    "insufficient_funds": "Недостаточно средств на счёте",
    "recipient_not_found": "Получатель с таким username не найден",
    "cannot_transfer_to_self": "Нельзя перевести деньги самому себе",
    "user_inactive": "Аккаунт деактивирован",
    "validation_error": "Некорректные данные запроса",
}


def _raise_for_error(resp: requests.Response) -> None:
    try:
        payload = resp.json()
    except ValueError:
        payload = {}

    err = payload.get("error") if isinstance(payload, dict) else None
    if err:
        code = err.get("code", "unknown_error")
        message = RU_MESSAGES.get(code) or err.get("message") or "Неизвестная ошибка сервера"
        exc_class = ERROR_MAP.get(code, BankError)
        raise exc_class(message)

    if resp.status_code == 401:
        raise SessionExpired("Сессия истекла. Войдите заново.")
    raise BankError(f"Ошибка сервера (код {resp.status_code})")


def _request(method: str, path: str, token: str = None, **kwargs) -> dict:
    url = f"{API_BASE_URL}{path}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.request(method, url, headers=headers, timeout=10, **kwargs)
    except requests.exceptions.ConnectionError:
        raise BankError(
            f"Не удаётся подключиться к серверу ({API_BASE_URL}). "
            "Убедитесь, что бэкенд друга запущен."
        )
    except requests.exceptions.Timeout:
        raise BankError("Сервер не отвечает (таймаут).")

    if resp.status_code >= 400:
        _raise_for_error(resp)

    return resp.json() if resp.content else {}


def signup(name: str, username: str, password: str) -> dict:
    return _request(
        "POST", "/auth/signup",
        json={"name": name, "username": username, "password": password},
    )


def login(username: str, password: str) -> dict:
    # ВАЖНО: /auth/login у друга принимает данные как HTML-форму
    # (OAuth2PasswordRequestForm), а не JSON!
    return _request(
        "POST", "/auth/login",
        data={"username": username, "password": password},
    )


def me(token: str) -> dict:
    return _request("GET", "/me", token=token)


def get_balance(token: str) -> dict:
    return _request("GET", "/account/balance", token=token)


def deposit(token: str, amount: float) -> dict:
    return _request("POST", "/account/deposit", token=token, json={"amount": amount})


def withdraw(token: str, amount: float) -> dict:
    return _request("POST", "/account/withdraw", token=token, json={"amount": amount})


def transfer(token: str, to_username: str, amount: float, comment: str = None) -> dict:
    return _request(
        "POST", "/account/transfer", token=token,
        json={"to_username": to_username, "amount": amount, "comment": comment},
    )


def list_transactions(token: str, limit: int = 5) -> list:
    return _request("GET", f"/transactions?limit={limit}", token=token)
