from django.apps import AppConfig


class LivePricingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "live_pricing"

    def ready(self):
        import live_pricing.signals