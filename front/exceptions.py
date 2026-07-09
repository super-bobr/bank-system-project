class BankError(Exception):
    """Базовое исключение для всех ожидаемых ошибок бизнес-логики.

    Всё, что наследуется от BankError, ловится в main.py и печатается
    пользователю как понятное сообщение (без traceback).
    """


class ValidationError(BankError):
    """Некорректный ввод пользователя (сумма, формат телефона и т.п.)."""


class InvalidCredentials(BankError):
    """Неверный логин/телефон или пароль при входе."""


class DuplicateUserError(BankError):
    """Пользователь с таким логином/телефоном уже существует."""


class UserNotFound(BankError):
    """Получатель перевода не найден."""


class InsufficientFunds(BankError):
    """Недостаточно средств для снятия или перевода."""


class SessionExpired(BankError):
    """Токен сессии истёк или не найден — нужно залогиниться заново."""


class UserInactive(BankError):
    """Аккаунт деактивирован на сервере."""


class SelfTransferError(BankError):
    """Попытка перевести деньги самому себе."""
