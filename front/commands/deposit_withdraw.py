import api_client
from validators import validate_amount


def deposit(token: str, amount) -> float:
    amt = float(validate_amount(amount))
    data = api_client.deposit(token, amt)
    return float(data["balance"])


def withdraw(token: str, amount) -> float:
    amt = float(validate_amount(amount))
    data = api_client.withdraw(token, amt)
    return float(data["balance"])
