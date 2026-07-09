# Colony Bank — клиентская часть (GUI)

Реализует: авторизацию с хранением токена, баланс, пополнение/снятие,
перевод по username, историю 5 последних операций, профиль, обработку
ошибок API.

## Архитектура
```
Твой GUI (gui/app.py)
   -> commands/*.py  (баланс, перевод, история...)
   -> auth.py         (регистрация, вход, проверка токена)
   -> api_client.py    (HTTP-запросы + разбор ошибок)
   -> backend/  (FastAPI, слушает на localhost:8000)
   -> PostgreSQL (база друга)
```

## Установка и запуск

### 1. Бэкенд

```bash
cd backend
pip install -r requirements.txt

# создать .env:
cat > .env << 'ENVEOF'
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/bankapi
SECRET_KEY=change-me-to-something-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVEOF

# в PostgreSQL создать пустую базу (таблицы создаются сами при старте):
createdb bankapi

python3 -m uvicorn app.main:app --reload --port 8000
```

Проверка: `curl http://localhost:8000/health` → `{"status":"ok"}`.

### 2. Клиент (GUI)

```bash
pip install -r requirements.txt   # requests
python3 gui/app.py
```

По умолчанию клиент стучится в `http://localhost:8000`. Если бэкенд
слушает на другом адресе — задай переменную окружения:

```bash
export BANK_API_URL=http://адрес:8000
```

CLI-версия для отладки без GUI: `python3 main.py`.

## Структура клиента

```
config.py            # адрес API (BANK_API_URL), путь к файлу сессии
api_client.py         # HTTP-запросы к API, коды ошибок -> BankError
exceptions.py         # BankError и подклассы — единая обработка ошибок
validators.py         # проверка сумм на клиенте (до отправки на сервер)
auth.py               # регистрация (авто-вход), вход, проверка токена
session.py            # хранение токена локально (~/.bank_cli/session.json)
main.py               # CLI-меню (для отладки)
gui/app.py            # Desktop GUI — основной интерфейс проекта
commands/
    balance.py         # GET /account/balance
    deposit_withdraw.py # POST /account/deposit, /account/withdraw
    transfer.py          # POST /account/transfer (по username)
    history.py            # GET /transactions
    profile.py             # GET /me + баланс
backend/         # копия бэкенда для локального запуска и тестов
```
запущенный API друга на localhost:8000): регистрация с авто-входом,
пополнение, снятие, перевод между двумя пользователями, история,
профиль, обработка трёх ошибок (получатель не найден, недостаточно
средств, неверный пароль — все на русском), сохранение сессии между
перезапусками приложения.
