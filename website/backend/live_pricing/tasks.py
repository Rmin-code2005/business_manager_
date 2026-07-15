from celery import shared_task
from django.core.cache import cache
from asgiref.sync import async_to_sync

from .clients import NerkhClient
from .cache import (
    CURRENCY_CACHE_KEY,
    GOLD_CACHE_KEY,
    CRYPTO_CACHE_KEY,
    PRICE_CACHE_TIMEOUT,
)



def save_price(key, data):

    cache.set(
        key,
        data,
        PRICE_CACHE_TIMEOUT
    )



@shared_task(
    name="live_pricing.refresh_prices"
)
def refresh_prices():

    client = NerkhClient()


    # Currency
    try:

        currency = async_to_sync(client.get)(
            "/v1/prices/json/currency"
        )

        save_price(
            CURRENCY_CACHE_KEY,
            currency
        )

    except Exception as e:

        print(
            f"Currency update failed: {e}"
        )



    # Gold
    try:

        gold = async_to_sync(client.get)(
            "/v1/prices/json/gold"
        )

        save_price(
            GOLD_CACHE_KEY,
            gold
        )

    except Exception as e:

        print(
            f"Gold update failed: {e}"
        )



    # Crypto
    try:

        crypto = async_to_sync(client.get)(
            "/v1/prices/json/crypto"
        )

        save_price(
            CRYPTO_CACHE_KEY,
            crypto
        )

    except Exception as e:

        print(
            f"Crypto update failed: {e}"
        )


    return "Prices refreshed"