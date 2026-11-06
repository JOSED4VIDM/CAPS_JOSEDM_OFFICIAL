from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def cop(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return "No disponible"
    if not amount.is_finite():
        return "No disponible"

    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"COP {formatted}"
