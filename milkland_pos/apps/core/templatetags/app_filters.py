from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def currency(value):
    try:
        return f"PKR {Decimal(value):,.2f}"
    except Exception:
        return value


@register.filter
def multiply(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except Exception:
        return 0


@register.filter
def subtract(value, arg):
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except Exception:
        return 0


@register.filter
def percentage(value, total):
    try:
        if Decimal(str(total)) == 0:
            return 0
        return round((Decimal(str(value)) / Decimal(str(total))) * 100, 1)
    except Exception:
        return 0


@register.filter
def absolute(value):
    try:
        return abs(Decimal(str(value)))
    except Exception:
        return value
