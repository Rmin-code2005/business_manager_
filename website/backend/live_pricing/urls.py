from django.urls import path

from .views import (
    SymbolsView,

    CurrencyPricesView,
    CurrencyPriceView,

    GoldPricesView,
    GoldPriceView,

    CryptoPricesView,
    CryptoPriceView,

    AllUserCurrencyBaskets,
    AllUserGoldBaskets,
    AllUserCryptoBaskets,
    
    SpeceficCurrencyBasketView,
    SpeceficCryptoBasketView,
    SpeceficGoldBasketView,
    IncreaseBasket,
    DecreaseBasket,
)

urlpatterns = [
    # -------------------------
    # Symbols
    # -------------------------
    path(
        "symbols/",
        SymbolsView.as_view(),
        name="symbols",
    ),

    # -------------------------
    # Currency
    # -------------------------
    path(
        "currency/prices/",
        CurrencyPricesView.as_view(),
        name="currency-all-prices",
    ),
    path(
        "currency/prices/<str:symbol>/",
        CurrencyPriceView.as_view(),
        name="currency-symbol-price",
    ),

    # -------------------------
    # Gold
    # -------------------------
    path(
        "gold/prices/",
        GoldPricesView.as_view(),
        name="gold-all-prices",
    ),
    path(
        "gold/prices/<str:symbol>/",
        GoldPriceView.as_view(),
        name="gold-symbol-price",
    ),

    # -------------------------
    # Crypto
    # -------------------------
    path(
        "crypto/prices/",
        CryptoPricesView.as_view(),
        name="crypto-all-prices",
    ),
    path(
        "crypto/prices/<str:symbol>/",
        CryptoPriceView.as_view(),
        name="crypto-symbol-price",
    ),

    # -------------------------
    # User Baskets
    # -------------------------
    path(
        "user/currency-basket/",
        AllUserCurrencyBaskets.as_view(),
        name="user-currency-basket",
    ),
    path(
        "user/gold-basket/",
        AllUserGoldBaskets.as_view(),
        name="user-gold-basket",
    ),
    path(
        "user/crypto-basket/",
        AllUserCryptoBaskets.as_view(),
        name="user-crypto-basket",
    ),
    path(
        "user/currency-basket/<str:symbol>",
        SpeceficCurrencyBasketView.as_view(),
        name = 'specefic-currency-basket'
    ),
    path(
        "user/gold-basket/<str:symbol>",
        SpeceficGoldBasketView.as_view(),
        name = 'specefic-gold-basket'
    ),
    path(
        "user/crypto-basket/<str:symbol>",
        SpeceficCryptoBasketView.as_view(),
        name = 'specefic-crypto-basket'
    ),
    path('user/basket/increase/', IncreaseBasket.as_view(), name='basket-increase'),
    path('user/basket/decrease/', DecreaseBasket.as_view(), name='basket-decrease'),
]