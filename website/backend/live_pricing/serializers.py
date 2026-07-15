from rest_framework import serializers
from django.db.models import Sum
from .models import CashBasket, GoldBasket, CryptoBasket, Price
from .validator import GOLD_SYMBOLS , CRYPTO_SYMBOLS , CURRENCY_SYMBOLS

class PriceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = (
            "id",
            "count",
            "start_price_T",
            "start_price_D",
            "created_at",
        )


class BaseBasketSerializer(serializers.ModelSerializer):
    start_price_T = serializers.SerializerMethodField()
    start_price_D = serializers.SerializerMethodField()
    # در صورت نیاز می‌توانید تاریخچه تغییرات قیمت این بسکت را هم در خروجی ببینید:
    price_logs = PriceLogSerializer(source="prices", many=True, read_only=True)

    class Meta:
        fields = (
            "id",
            "name",
            "count",
            "start_price_T",
            "start_price_D",
            "price_logs",
        )

    def get_start_price_T(self, obj):
        # جمع مبالغ تومانی تمام تراکنش‌های فعال این بسکت
        result = obj.prices.filter(is_deleted=False).aggregate(total=Sum('start_price_T'))
        return result['total'] or 0.0

    def get_start_price_D(self, obj):
        # جمع مبالغ دلاری تمام تراکنش‌های فعال این بسکت
        result = obj.prices.filter(is_deleted=False).aggregate(total=Sum('start_price_D'))
        return result['total'] or 0.0


class BaseGeneralBasketSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name",)


class CurrencyBasketSerializer(BaseBasketSerializer):
    class Meta(BaseBasketSerializer.Meta):
        model = CashBasket 


class CryptoBasketSerializer(BaseBasketSerializer):
    class Meta(BaseBasketSerializer.Meta):
        model = CryptoBasket


class GoldBasketSerializer(BaseBasketSerializer):
    class Meta(BaseBasketSerializer.Meta):
        model = GoldBasket


class GeneralCurrencyBasketSerializer(BaseGeneralBasketSerializer):
    class Meta(BaseGeneralBasketSerializer.Meta):
        model = CashBasket 


class GeneralCryptoBasketSerializer(BaseGeneralBasketSerializer):
    class Meta(BaseGeneralBasketSerializer.Meta):
        model = CryptoBasket


class GeneralGoldBasketSerializer(BaseGeneralBasketSerializer):
    class Meta(BaseGeneralBasketSerializer.Meta):
        model = GoldBasket
        
class ChangeBasketValueSerializer(serializers.Serializer):
    type = serializers.CharField()      # می تواند ca (نقد), cr (کریپتو) یا g (طلا) باشد
    symbol = serializers.CharField()
    value = serializers.DecimalField(max_digits=20, decimal_places=8)

    def validate_type(self, value):
        valid_types = ['ca', 'cr', 'g']
        if value not in valid_types:
            raise serializers.ValidationError(f"Type should be one of {valid_types}")
        return value

    def validate(self, attrs):
        basket_type = attrs.get('type')
        symbol = attrs.get('symbol')

        if basket_type == 'ca' and symbol not in CURRENCY_SYMBOLS:
            raise serializers.ValidationError({"symbol": f"'{symbol}' is not a valid currency symbol."})
        
        elif basket_type == 'cr' and symbol not in CRYPTO_SYMBOLS:
            raise serializers.ValidationError({"symbol": f"'{symbol}' is not a valid crypto symbol."})
        
        elif basket_type == 'g' and symbol not in GOLD_SYMBOLS:
            raise serializers.ValidationError({"symbol": f"'{symbol}' is not a valid gold symbol."})

        # بررسی اینکه مقدار تراکنش حتما مثبت باشد
        if attrs.get('value') <= 0:
            raise serializers.ValidationError({"value": "Value must be greater than zero."})

        return attrs
