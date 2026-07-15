import re
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

TELEGRAM_USERNAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$")

def validate_iran_phone(value):
    pattern = r'^(09\d{9}|9\d{9})$'

    if not re.fullmatch(pattern, value):
        raise ValidationError(
            "Phone number must start with 9 or 09."
        )       

def validate_telegram_username(value):
    if not value:
        return

    username = value.lstrip("@")

    if not TELEGRAM_USERNAME_REGEX.fullmatch(username):
        raise ValidationError(
            _(
                "Telegram username must start with a letter and contain only "
                "letters, numbers and underscores (5-32 characters)."
            )
        )