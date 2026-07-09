import api_client


def get_balance(token: str) -> float:
    data = api_client.get_balance(token)
    return float(data["balance"])
