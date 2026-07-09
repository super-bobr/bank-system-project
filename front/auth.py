"""Авторизация через API друга. Токен — это JWT, который выдаёт сервер;
здесь мы его просто передаём дальше и не генерируем сами (в отличие от
старой версии с прямым доступом к БД).
"""

import api_client
from exceptions import ValidationError


def register(name: str, username: str, password: str) -> str:
    """Регистрирует пользователя и возвращает токен (сервер сразу логинит)."""
    name = name.strip()
    username = username.strip()
    if not name:
        raise ValidationError("Имя не может быть пустым")
    if len(username) < 3:
        raise ValidationError("Логин должен быть не короче 3 символов")
    if len(password) < 6:
        raise ValidationError("Пароль должен быть не короче 6 символов")

    data = api_client.signup(name, username, password)
    return data["access_token"]


def login(username: str, password: str) -> str:
    data = api_client.login(username.strip(), password)
    return data["access_token"]


def logout(token: str) -> None:
    # У API друга нет эндпоинта logout — токен JWT stateless, отозвать его
    # на сервере нельзя. Просто перестаём использовать токен на клиенте.
    pass


def verify_token(token: str) -> dict:
    """Проверяет токен через GET /me. Бросает SessionExpired, если невалиден."""
    return api_client.me(token)
