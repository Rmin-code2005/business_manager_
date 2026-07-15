from decimal import Decimal
from asgiref.sync import async_to_sync
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

# سه تا تابع جدا برای سه نوع دارایی: ارز، طلا، کریپتو
from live_pricing.services import (
    get_price_by_symbol,
    get_gold_by_symbol,
    get_crypto_by_symbol,
)

from .models import CashBasket, GoldBasket, CryptoBasket, Price


def record_price_change(instance, delta_count):
    """
    محاسبه قیمت لحظه‌ای بر اساس مقدار تغییر یافته و ثبت در جدول قیمت‌ها
    """
    if delta_count == 0:
        return

    # انتخاب تابع درست بر اساس نوع بسکت (قبلاً همیشه از تابع Currency
    # استفاده می‌شد که باعث می‌شد کریپتو و طلا با خطای
    # "Currency 'XXX' not found" مواجه بشن)
    if isinstance(instance, CashBasket):
        price_fn = get_price_by_symbol
    elif isinstance(instance, GoldBasket):
        price_fn = get_gold_by_symbol
    elif isinstance(instance, CryptoBasket):
        price_fn = get_crypto_by_symbol
    else:
        raise ValueError(f"Unknown basket type: {type(instance)}")

    # گرفتن قیمت لحظه‌ای دارایی با تابع مخصوص همون نوع دارایی
    asset_price_data = price_fn(instance.name)

    # قیمت دلار همیشه باید از سرویس ارز گرفته شود (USD یک ارز است)
    usd_price_data = get_price_by_symbol("USD")

    asset_unit_price = Decimal(str(asset_price_data["price"]))
    usd_unit_price = Decimal(str(usd_price_data["price"]))

    # محاسبه ارزش تومانی و دلاریِ این مقدارِ تغییر یافته
    amount_in_T = asset_unit_price * delta_count
    amount_in_D = amount_in_T / usd_unit_price

    # تشخیص نوع بسکت برای پر کردن کلید خارجی مناسب
    price_kwargs = {
        "count": delta_count,
        "start_price_T": amount_in_T,
        "start_price_D": amount_in_D,
    }

    if isinstance(instance, CashBasket):
        price_kwargs["cash_basket"] = instance
    elif isinstance(instance, GoldBasket):
        price_kwargs["gold_basket"] = instance
    elif isinstance(instance, CryptoBasket):
        price_kwargs["crypto_basket"] = instance

    # ایجاد یک رکورد جدید در جدول قیمت‌ها به عنوان تاریخچه این تغییر
    Price.objects.create(**price_kwargs)


# -----------------------------
# Pre Save (ذخیره وضعیت قبلی برای مقایسه تغییرات)
# -----------------------------

@receiver(pre_save, sender=CashBasket)
@receiver(pre_save, sender=GoldBasket)
@receiver(pre_save, sender=CryptoBasket)
def remember_old_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_count = Decimal("0")
        instance._old_is_deleted = False
        return

    old = sender.objects.filter(pk=instance.pk).first()
    if old is None:
        instance._old_count = Decimal("0")
        instance._old_is_deleted = False
        return

    instance._old_count = Decimal(str(old.count))
    instance._old_is_deleted = old.is_deleted


# -----------------------------
# Post Save (ثبت تراکنش قیمت‌ها و حذف خودکار بسکت‌های خالی)
# -----------------------------

@receiver(post_save, sender=CashBasket)
@receiver(post_save, sender=GoldBasket)
@receiver(post_save, sender=CryptoBasket)
def price_signal(sender, instance, created, **kwargs):
    # ۱. زمان ساخت بسکت جدید
    if created:
        if instance.count > 0:
            record_price_change(instance, Decimal(str(instance.count)))
        elif instance.count <= 0:
            # اگر بسکتی با موجودی صفر یا کمتر ساخته شد، بلافاصله سافت دیلیت شود
            instance.delete()
        return

    # ۲. سافت دیلیت شدن بسکت (جلوگیری از حلقه بی‌نهایت هنگام حذف)
    if instance.is_deleted and not instance._old_is_deleted:
        instance.prices.all().delete()
        return

    # ۳. ریستور و بازگردانی بسکت
    if not instance.is_deleted and instance._old_is_deleted:
        for p in instance.prices.all():
            p.restore()
        return

    # اگر بسکت از قبل حذف شده باشد، تغییرات بعدی نادیده گرفته می‌شود
    if instance.is_deleted:
        return

    # ۴. بررسی رسیدن دارایی به صفر یا کمتر
    new_count = Decimal(str(instance.count))
    if new_count <= 0:
        # ثبت آخرین تغییر تراکنش قبل از حذف (کم شدن باقی‌مانده موجودی تا صفر)
        if instance._old_count > 0:
            delta = Decimal("0") - instance._old_count
            record_price_change(instance, delta)

        # حذف (سافت دیلیت) خودکار بسکت
        instance.delete()
        return

    # ۵. تغییر معمولی مقدار عددی موجودی بسکت (کم یا زیاد شدن عادی)
    if new_count != instance._old_count:
        delta = new_count - instance._old_count
        record_price_change(instance, delta)