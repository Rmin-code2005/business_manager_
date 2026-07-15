from django.core.cache import cache

CURRENCY_CACHE_KEY = "prices:currency"
GOLD_CACHE_KEY = "prices:gold"
CRYPTO_CACHE_KEY = "prices:crypto"

PRICE_CACHE_TIMEOUT = 60 * 60 * 2   # دو ساعت