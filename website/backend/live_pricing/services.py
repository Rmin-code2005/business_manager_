from django.core.cache import cache
from rest_framework.exceptions import NotFound, APIException

from .cache import (
    CURRENCY_CACHE_KEY,
    GOLD_CACHE_KEY,
    CRYPTO_CACHE_KEY,
)


def _get_cache(key: str):

    data = cache.get(key)

    if data is None:
        raise APIException(
            detail="Price cache is empty. Please wait for price updater."
        )

    return data



def get_all_currency_prices():

    return _get_cache(CURRENCY_CACHE_KEY)



def get_price_by_symbol(symbol: str):

    data = get_all_currency_prices()

    prices = data["data"]["prices"]

    symbol = symbol.upper()

    if symbol not in prices:
        raise NotFound(
            detail=f"Currency '{symbol}' not found."
        )

    return {
        "symbol": symbol,
        "price": prices[symbol]["min"]["1hour"]
    }



def get_all_gold():

    return _get_cache(GOLD_CACHE_KEY)



def get_gold_by_symbol(symbol: str):

    data = get_all_gold()

    prices = data["data"]["prices"]

    symbol = symbol.upper()

    if symbol not in prices:
        raise NotFound(
            detail=f"Gold symbol '{symbol}' not found."
        )

    return {
        "symbol": symbol,
        "price": prices[symbol]["min"]["1hour"]
    }



def get_all_crypto():

    return _get_cache(CRYPTO_CACHE_KEY)



def get_crypto_by_symbol(symbol: str):

    data = get_all_crypto()

    prices = data["data"]["prices"]

    symbol = symbol.upper()

    if symbol not in prices:
        raise NotFound(
            detail=f"Crypto symbol '{symbol}' not found."
        )

    return {
        "symbol": symbol,
        "price": prices[symbol]["min"]["1hour"]
    }