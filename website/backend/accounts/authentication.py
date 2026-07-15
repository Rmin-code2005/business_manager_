# accounts/authentication.py

from rest_framework.authentication import BaseAuthentication
from accounts.models import CustomUser


class TelegramAuthentication(BaseAuthentication):

    def authenticate(self, request):

        token = request.headers.get("X-Telegram-Token")

        if not token:
            return None

        try:
            user = CustomUser.objects.get(telegram_token=token)
        except CustomUser.DoesNotExist:
            return None

        return (user, None)