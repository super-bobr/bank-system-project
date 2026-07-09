import api_client


def get_profile(token: str) -> dict:
    """Профиль по API друга содержит только id/name/username (нет телефона
    и даты регистрации — их просто нет в UserResponse на бэкенде).
    """
    user = api_client.me(token)
    balance_data = api_client.get_balance(token)
    return {
        "name": user["name"],
        "username": user["username"],
        "balance": float(balance_data["balance"]),
        "currency": balance_data.get("currency", "RUB"),
    }
