from asgiref.sync import async_to_sync

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView , get_object_or_404 
from rest_framework import status 
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from .models import (
    CashBasket,
    GoldBasket,
    CryptoBasket,
)

from .serializers import (
    CurrencyBasketSerializer,
    GoldBasketSerializer,
    CryptoBasketSerializer,
    GeneralCryptoBasketSerializer,
    GeneralCurrencyBasketSerializer,
    GeneralGoldBasketSerializer,
    ChangeBasketValueSerializer
)

from .services import (
    get_all_currency_prices,
    get_price_by_symbol,
    get_all_gold,
    get_gold_by_symbol,
    get_all_crypto,
    get_crypto_by_symbol,
)

from .validator import (
    CURRENCY_SYMBOLS,
    GOLD_SYMBOLS,
    CRYPTO_SYMBOLS,
)


# =========================
# Symbols
# =========================

class SymbolsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(
            {
                "currency": CURRENCY_SYMBOLS,
                "gold": GOLD_SYMBOLS,
                "crypto": CRYPTO_SYMBOLS,
            }
        )


# =========================
# Currency Prices
# =========================

class CurrencyPricesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict, operation_id="currency_prices_all_list")
    def get(self, request):
        return Response(
            get_all_currency_prices()
        )

class CurrencyPriceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict, operation_id="currency_prices_single_retrieve")
    def get(self, request, symbol):
        return Response(
            get_price_by_symbol(symbol)
        )


# =========================
# Gold Prices
# =========================

class GoldPricesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict, operation_id="gold_prices_all_list")
    def get(self, request):
        return Response(
            get_all_gold()
        )


class GoldPriceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict, operation_id="gold_prices_single_retrieve")
    def get(self, request, symbol):
        return Response(
            get_gold_by_symbol(symbol)
        )


# =========================
# Crypto Prices
# =========================

class CryptoPricesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict, operation_id="crypto_prices_all_list")
    def get(self, request):
        return Response(
            get_all_crypto()
        )


class CryptoPriceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict, operation_id="crypto_prices_single_retrieve")
    def get(self, request, symbol):
        return Response(
            get_crypto_by_symbol(symbol)
        )


# =========================
# User Baskets
# =========================

class AllUserCurrencyBaskets(ListAPIView):
    serializer_class = GeneralCurrencyBasketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CashBasket.alive_objects
            .filter(user=self.request.user)
            .prefetch_related("prices")
        )


class AllUserGoldBaskets(ListAPIView):
    serializer_class = GeneralGoldBasketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            GoldBasket.alive_objects
            .filter(user=self.request.user)
            .prefetch_related("prices")
        )


class AllUserCryptoBaskets(ListAPIView):
    serializer_class = GeneralCryptoBasketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CryptoBasket.alive_objects
            .filter(user=self.request.user)
            .prefetch_related("prices")
        )


class SpeceficCurrencyBasketView(RetrieveAPIView):
    serializer_class = CurrencyBasketSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return CashBasket.alive_objects.get(name=self.kwargs['symbol'], user=self.request.user)


class SpeceficGoldBasketView(RetrieveAPIView):
    serializer_class = GoldBasketSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return GoldBasket.alive_objects.get(name=self.kwargs['symbol'], user=self.request.user)


class SpeceficCryptoBasketView(RetrieveAPIView):
    serializer_class = CryptoBasketSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return CryptoBasket.alive_objects.get(name=self.kwargs['symbol'], user=self.request.user)


# =========================
# Action Baskets (Increase / Decrease)
# =========================

class IncreaseBasket(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeBasketValueSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        basket_type = serializer.validated_data['type']
        symbol = serializer.validated_data['symbol']
        value = serializer.validated_data['value']
        user = self.request.user

        if basket_type == 'ca':
            model_class = CashBasket
        elif basket_type == 'cr':
            model_class = CryptoBasket
        else:
            model_class = GoldBasket


        basket_obj = model_class.alive_objects.filter(user=user, name=symbol).first()

        if basket_obj:
            basket_obj.count += value
            basket_obj.save()
        else:
           
            basket_obj = model_class.objects.filter(user=user, name=symbol).first()
            if basket_obj:
                basket_obj.restore()
                basket_obj.count += value
                basket_obj.save()
            else:
              
                basket_obj = model_class.objects.create(
                    user=user,
                    name=symbol,
                    count=value
                )

        return Response(
            {"detail": f"Successfully increased {symbol} basket by {value}."},
            status=status.HTTP_200_OK
        )


class DecreaseBasket(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeBasketValueSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        basket_type = serializer.validated_data['type']
        symbol = serializer.validated_data['symbol']
        value = serializer.validated_data['value']
        user = self.request.user

        if basket_type == 'ca':
            model_class = CashBasket
        elif basket_type == 'cr':
            model_class = CryptoBasket
        else:
            model_class = GoldBasket


        basket_obj = model_class.alive_objects.filter(user=user, name=symbol).first()

        if basket_obj:
            basket_obj.count -= value
            basket_obj.save()
        else:
           
            basket_obj = model_class.objects.filter(user=user, name=symbol).first()
            if basket_obj:
                basket_obj.restore()
                basket_obj.count -= value
                basket_obj.save()
            

        return Response(
            {"detail": f"Successfully increased {symbol} basket by {value}."},
            status=status.HTTP_200_OK
        )