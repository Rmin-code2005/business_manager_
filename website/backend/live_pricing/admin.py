from django.contrib import admin
from django.db.models import Sum
from .models import (
    Price,
    CashBasket,
    GoldBasket,
    CryptoBasket,
)
from .filters import SoftDeleteFilter
from .actions import (
    soft_delete_baskets,
    restore_baskets,
    hard_delete_baskets,
)

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.alive_objects.all()

    list_display = (
        "id",
        "basket_info",
        "count",
        "start_price_T",
        "start_price_D",
        "created_at",
    )

    ordering = ("-id",)
    search_fields = ("id", "cash_basket__name", "gold_basket__name", "crypto_basket__name")
    readonly_fields = ("count", "start_price_T", "start_price_D", "cash_basket", "gold_basket", "crypto_basket")

    def has_add_permission(self, request):
        return False

    @admin.display(description="Basket")
    def basket_info(self, obj):
        return str(obj.basket)


class BaseBasketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "count",
        "deleted",
        "start_price_t",
        "start_price_d",
    )

    search_fields = (
        "name",
        "user__email",
        "user__phone",
    )

    ordering = ("-id",)
    autocomplete_fields = ("user",)
    list_filter = (SoftDeleteFilter, "name")

    actions = (
        soft_delete_baskets,
        restore_baskets,
        hard_delete_baskets,
    )

    def get_queryset(self, request):
        # استفاده از prefetch_related به جای select_related به خاطر رابطه یک به چند قیمت‌ها
        return self.model.objects.select_related("user").prefetch_related("prices")

    @admin.display(boolean=True, description="Deleted")
    def deleted(self, obj):
        return obj.is_deleted

    @admin.display(description="Total Price (T)")
    def start_price_t(self, obj):
        total = obj.prices.filter(is_deleted=False).aggregate(Sum('start_price_T'))['start_price_T__sum']
        return total if total is not None else "-"

    @admin.display(description="Total Price ($)")
    def start_price_d(self, obj):
        total = obj.prices.filter(is_deleted=False).aggregate(Sum('start_price_D'))['start_price_D__sum']
        return total if total is not None else "-"


@admin.register(CashBasket)
class CashBasketAdmin(BaseBasketAdmin):
    pass


@admin.register(GoldBasket)
class GoldBasketAdmin(BaseBasketAdmin):
    pass


@admin.register(CryptoBasket)
class CryptoBasketAdmin(BaseBasketAdmin):
    pass