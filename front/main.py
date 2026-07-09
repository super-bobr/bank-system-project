import sys

import requests

import auth
import session
from exceptions import BankError, SessionExpired
from commands.balance import get_balance
from commands.deposit_withdraw import deposit, withdraw
from commands.transfer import transfer
from commands.history import last_transactions
from commands.profile import get_profile

TYPE_LABELS = {
    "deposit": "Пополнение",
    "withdraw": "Снятие",
    "transfer_in": "Перевод от",
    "transfer_out": "Перевод для",
}


def require_token():
    """Возвращает валидный токен либо None, если пользователь не авторизован
    или сессия истекла. Единая точка входа для проверки авторизации в CLI.
    """
    token = session.load_token()
    if not token:
        print("Вы не авторизованы. Сначала выполните вход (пункт 2).")
        return None
    try:
        auth.verify_token(token)
    except SessionExpired as e:
        session.clear_token()
        print(f"{e}")
        return None
    return token


def cmd_register():
    print("--- Регистрация ---")
    name = input("Имя: ").strip()
    username = input("Логин: ").strip()
    password = input("Пароль (от 6 символов): ").strip()
    try:
        token = auth.register(name, username, password)
        session.save_token(token)
        print("✅ Аккаунт создан, вы уже вошли в систему.")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_login():
    print("--- Вход ---")
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()
    try:
        token = auth.login(username, password)
        session.save_token(token)
        print("Вход выполнен успешно.")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_logout():
    token = session.load_token()
    if token:
        try:
            auth.logout(token)
        except BankError:
            pass
        session.clear_token()
    print("Вы вышли из системы.")


def cmd_balance():
    token = require_token()
    if not token:
        return
    try:
        bal = get_balance(token)
        print(f"Ваш баланс: {bal:.2f} \u20bd")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_deposit():
    token = require_token()
    if not token:
        return
    amount = input("Сумма пополнения: ").strip()
    try:
        new_balance = deposit(token, amount)
        print(f"Пополнено. Новый баланс: {new_balance:.2f} \u20bd")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_withdraw():
    token = require_token()
    if not token:
        return
    amount = input("Сумма снятия: ").strip()
    try:
        new_balance = withdraw(token, amount)
        print(f"Снято. Новый баланс: {new_balance:.2f} \u20bd")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_transfer():
    token = require_token()
    if not token:
        return
    target = input("Кому переводим (username получателя): ").strip()
    amount = input("Сумма перевода: ").strip()
    try:
        result = transfer(token, target, amount)
        print(f"Переведено {result['amount']:.2f} \u20bd пользователю {result['target']}.")
        print(f"Ваш новый баланс: {result['new_balance']:.2f} \u20bd")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_history():
    token = require_token()
    if not token:
        return
    try:
        rows = last_transactions(token, limit=5)
        if not rows:
            print("История операций пуста.")
            return
        print("Последние 5 операций:")
        for r in rows:
            label = TYPE_LABELS.get(r["type"], r["type"])
            counterparty = f" ({r['counterparty_username']})" if r["counterparty_username"] else ""
            print(f"  {r['created_at']:%Y-%m-%d %H:%M}  {label}{counterparty}: {r['amount']:.2f} \u20bd")
    except BankError as e:
        print(f"Ошибка: {e}")


def cmd_profile():
    token = require_token()
    if not token:
        return
    try:
        p = get_profile(token)
        print("--- Профиль ---")
        print(f"Имя: {p['name']}")
        print(f"Логин: {p['username']}")
        print(f"Баланс: {p['balance']:.2f} {p['currency']}")
    except BankError as e:
        print(f"Ошибка: {e}")


MENU = """
==================== Colony Bank CLI ====================
1. Регистрация
2. Вход
3. Баланс
4. Пополнить
5. Снять
6. Перевести пользователю
7. История (5 последних операций)
8. Профиль
0. Выйти из аккаунта (logout)
9. Закрыть программу
===========================================================
"""

ACTIONS = {
    "1": cmd_register,
    "2": cmd_login,
    "3": cmd_balance,
    "4": cmd_deposit,
    "5": cmd_withdraw,
    "6": cmd_transfer,
    "7": cmd_history,
    "8": cmd_profile,
    "0": cmd_logout,
}


def main():
    while True:
        print(MENU)
        choice = input("Выберите пункт: ").strip()
        if choice == "9":
            print("До встречи!")
            sys.exit(0)

        action = ACTIONS.get(choice)
        if not action:
            print("Неверный пункт меню. Попробуйте снова.")
            continue

        try:
            action()
        except requests.exceptions.ConnectionError:
            print("Не удаётся подключиться к серверу. Проверьте, что бэкенд друга запущен "
                  "(переменная окружения BANK_API_URL).")
        except Exception as e:  # неожиданная ошибка — не должна ронять всю программу
            print(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
