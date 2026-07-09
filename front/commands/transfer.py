import api_client
from validators import validate_amount


def transfer(token: str, target_username: str, amount, comment: str = None) -> dict:
    """Перевод по username. У API друга нет привязки к телефону — только
    username (см. app/schemas/account.py:TransferRequest в проекте друга).
    """
    target_username = target_username.strip()
    amt = float(validate_amount(amount))

    api_client.transfer(token, target_username, amt, comment)
    # Эндпоинт /account/transfer не возвращает новый баланс — запрашиваем отдельно.
    new_balance = float(api_client.get_balance(token)["balance"])

    return {"new_balance": new_balance, "target": target_username, "amount": amt}
