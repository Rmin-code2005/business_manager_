from django.core.cache import cache
from django.core.management.base import BaseCommand

from live_pricing.cache import CURRENCY_CACHE_KEY
from live_pricing.tasks import refresh_prices


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        if cache.get(CURRENCY_CACHE_KEY):
            self.stdout.write(
                "Price cache already exists."
            )
            return

        refresh_prices.delay()

        self.stdout.write(
            "Price refresh task sent."
        )