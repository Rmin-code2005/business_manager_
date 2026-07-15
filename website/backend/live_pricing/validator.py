from django.core.exceptions import ValidationError

CURRENCY_SYMBOLS = {
    "USD",
    "EUR",
    "GBP",
    "AED",
    "TRY",
}

CRYPTO_SYMBOLS = {
    "BTC",
    "ETH",
    "USDT",
    "XRP",
}

GOLD_SYMBOLS = {
    "GOLD18K",
    "GOLD24K",
    "MAZANEH",
    "OUNCE",
    "SEKE_1G",
    "SEKE_BAHAR",
    "SEKE_EMAMI",
    "SEKE_NIM",
    "SEKE_ROB",
    "SEKE_PRS100",
    "SEKE_PRS200",
    "SEKE_PRS400",
    "SEKE_PRS500",
    "SEKE_PRS700",
}


def validate_crypto_symbol(value):
    if value not in CRYPTO_SYMBOLS:
        raise ValidationError("Invalid crypto symbol.")
    
def validate_gold_symbol(value):
    if value not in GOLD_SYMBOLS:
        raise ValidationError("Invalid gold symbol.")
    
def validate_currency_symbol(value):
    if value not in CURRENCY_SYMBOLS:
        raise ValidationError("Invalid currency symbol.")