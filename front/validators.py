from decimal import Decimal, InvalidOperation

from exceptions import ValidationError


def validate_amount(amount) -> Decimal:
    try:
        amt = Decimal(str(amount).strip().replace(",", "."))
    except (InvalidOperation, ValueError, AttributeError):
        raise ValidationError("Сумма должна быть числом, например 1500.50")
    if amt <= 0:
        raise ValidationError("Сумма должна быть больше нуля")
    if amt.as_tuple().exponent < -2:
        raise ValidationError("Сумма не может иметь больше двух знаков после запятой")
    return amt
