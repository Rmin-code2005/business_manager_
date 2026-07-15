from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from .managers import AliveObjects
from .validator import (
    validate_currency_symbol,
    validate_gold_symbol,
    validate_crypto_symbol,
)

# -----------------------------
# Abstract Models
# -----------------------------

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    alive_objects = AliveObjects()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        if not self.is_deleted:
            return
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


# -----------------------------
# Base Basket (Abstract)
# -----------------------------

class BaseBasket(TimeStampedModel, SoftDeleteModel):
    # این فیلد موجودی کل بسکت را نگه می‌دارد و با سیگنال به روز می‌شود
    count = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        # سافت دیلیت کردن تمام قیمت‌های مربوطه
        self.prices.all().delete()
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        # بازگردانی تمام قیمت‌های مربوطه
        for price in self.prices.all():
            price.restore()
        super().restore()

    def hard_delete(self, using=None, keep_parents=False):
        # حذف فیزیکی تمام قیمت‌ها
        self.prices.all().hard_delete()
        super().hard_delete(using=using, keep_parents=keep_parents)


# -----------------------------
# Cash Basket
# -----------------------------

class CashBasket(BaseBasket):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="cash_baskets",
    )
    name = models.CharField(
        max_length=10,
        validators=[validate_currency_symbol],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="cashbasket_unique_symbol_per_user",
            )
        ]


# -----------------------------
# Gold Basket
# -----------------------------

class GoldBasket(BaseBasket):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="gold_baskets",
    )
    name = models.CharField(
        max_length=10,
        validators=[validate_gold_symbol],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="goldbasket_unique_symbol_per_user",
            )
        ]


# -----------------------------
# Crypto Basket
# -----------------------------

class CryptoBasket(BaseBasket):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="crypto_baskets",
    )
    name = models.CharField(
        max_length=10,
        validators=[validate_crypto_symbol],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="cryptobasket_unique_symbol_per_user",
            )
        ]


# -----------------------------
# Price (Transaction Log)
# -----------------------------

class Price(TimeStampedModel, SoftDeleteModel):
    # اتصال به بسکت‌ها (هر رکورد قیمت فقط به یکی از این‌ها متصل می‌شود)
    cash_basket = models.ForeignKey(
        CashBasket,
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )
    gold_basket = models.ForeignKey(
        GoldBasket,
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )
    crypto_basket = models.ForeignKey(
        CryptoBasket,
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )

    # مقداری که در این تراکنش اضافه یا کم شده است (مثلا ۵.۰۰ یا ۵.۰۰-)
    count = models.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    # قیمت تومانی و دلاریِ «کلِ مقدارِ این تراکنش» در لحظه ثبت
    start_price_T = models.DecimalField(
        max_digits=20,
        decimal_places=8,
    )
    start_price_D = models.DecimalField(
        max_digits=20,
        decimal_places=8,
    )

    @property
    def basket(self):
        return self.cash_basket or self.gold_basket or self.crypto_basket

    def __str__(self):
        return f"Change: {self.count} for {self.basket}"