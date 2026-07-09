import os

# Адрес API друга (FastAPI/uvicorn). Переопределяется переменной окружения,
# чтобы у тебя и у напарника были разные локальные настройки без правки кода.
API_BASE_URL = os.getenv("BANK_API_URL", "http://localhost:8000")

# Локальное хранение токена между запусками GUI/CLI
SESSION_FILE = os.path.expanduser("~/.bank_cli/session.json")
