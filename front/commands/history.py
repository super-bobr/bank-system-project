from datetime import datetime

import api_client

TYPE_LABELS = {
    "deposit": "Пополнение",
    "withdraw": "Снятие",
    "transfer_in": "Перевод от",
    "transfer_out": "Перевод для",
}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def last_transactions(token: str, limit: int = 5) -> list:
    """Возвращает последние операции в формате, понятном GUI/CLI.

    ВАЖНО: API отдаёт related_account_id (номер счёта получателя/
    отправителя), а не его username — эндпоинта для обратного поиска
    username по account_id в API нет. Поэтому в поле counterparty мы можем
    показать только "счёт #N", а не имя человека. Если это критично для
    практики — стоит попросить друга добавить username в ответ /transactions.
    """
    rows = api_client.list_transactions(token, limit=limit)
    result = []
    for r in rows:
        counterparty = f"счёт #{r['related_account_id']}" if r.get("related_account_id") else None
        result.append({
            "type": r["type"],
            "amount": float(r["amount"]),
            "counterparty_username": counterparty,
            "comment": r.get("comment"),
            "created_at": _parse_dt(r["created_at"]),
        })
    return result
