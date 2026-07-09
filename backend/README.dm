BankSim Backend

Учебный проект (летняя практика): backend для симулятора банковских операций.  
Стек: FastAPI, PostgreSQL, SQLAlchemy, JWT.

Возможности
- Регистрация и логин (JWT токен)
- /me — профиль текущего пользователя
- Баланс счёта
- Пополнение / снятие
- Перевод между пользователями по `username`
- История транзакций (последние N)

Требования
- Python 3.9+
- PostgreSQL (локально)
- Создана БД banksim и пользователь banksim_user

Настройка и запуск

1. Клонировать проект
git clone <URL_репозитория>
cd banksim_backend

2. Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

3. Зависимости
pip install -r requirements.txt

4. Создать .env в корне проекта
DATABASE_URL=postgresql+psycopg2://banksim_user:1111@localhost:5432/banksim
SECRET_KEY=CHANGE_ME_SUPER_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

5. Запуск
uvicorn app.main:app --reload

- Swagger UI: http://127.0.0.1:8000/docs  
- Healthcheck: http://127.0.0.1:8000/health  

> Таблицы создаются автоматически при старте приложения (SQLAlchemy create_all).

Как пользоваться (через Swagger)
1. POST /auth/signup или POST /auth/login → получить access_token  
2. Нажать Authorize и вставить только access_token (без кавычек и без Bearer)  
3. Вызывать защищённые методы (/me, /account/, /transactions)

Основные эндпоинты

Auth
- POST /auth/signup (JSON: name, username, password) → token
- POST /auth/login (form: username, password) → token

Account
- GET /me → текущий пользователь
- GET /account/balance → баланс
- POST /account/deposit (JSON: amount) → новый баланс
- POST /account/withdraw (JSON: amount) → новый баланс
- POST /account/transfer` (JSON: to_username, amount, comment?) → { "status": "ok" }

Transactions
- GET /transactions?limit=5 → последние транзакции

Формат ошибок (удобно для фронта)
Ошибки возвращаются в едином формате:

{
  "error": {
    "code": "insufficient_funds",
    "message": "Insufficient funds"
  }
}


Примеры error.code:
- username_taken
- invalid_credentials
- user_inactive
- insufficient_funds
- recipient_not_found
- cannot_transfer_to_self
- validation_error
