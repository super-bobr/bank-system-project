import json
import os
from typing import Optional

from config import SESSION_FILE


def save_token(token: str) -> None:
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"token": token}, f)


def load_token() -> Optional[str]:
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE) as f:
            return json.load(f).get("token")
    except (json.JSONDecodeError, OSError):
        return None


def clear_token() -> None:
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
