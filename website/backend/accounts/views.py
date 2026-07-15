from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LogoutSerializer , LoginSerializer , UserDetailSerializer , RegisterSerializer , UserTelegramUsernameUpdateSerializer,UserChangeInfoSerializer
from rest_framework.generics import RetrieveAPIView , CreateAPIView , UpdateAPIView
from django.shortcuts import get_object_or_404
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
import secrets

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    
    
class LogoutView(APIView):

    def post(self, request):

        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response(
            {"detail": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

class UserDetailView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    
class RegisterView(CreateAPIView):

    serializer_class = RegisterSerializer
    
class UserTelegramUsernameUpdateView(UpdateAPIView):
    serializer_class = UserTelegramUsernameUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
class UserChangeInfoView(UpdateAPIView):
    serializer_class = UserChangeInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
@api_view(["POST"])
def register_telegram(request):

    username = request.data.get("telegram_username")
    telegram_user_id = request.data.get("telegram_user_id")
    user = CustomUser.objects.filter(
    telegram_username=username
    ).first()
    if user is None:
        return Response(
        {"detail": "User not found"},
        status=404
        )

    # user.save(update_fields=["telegram_id"])
    another_user = CustomUser.objects.filter(
        telegram_id=telegram_user_id
    ).exclude(pk=user.pk).exists()

    if another_user:
        return Response(
        {"detail": "Telegram account already linked to another user."},
        status=status.HTTP_409_CONFLICT,
        )
    user.telegram_id = telegram_user_id
    user.telegram_token = secrets.token_hex(32)

    user.save(update_fields=["telegram_id", "telegram_token"])
    return Response(
        {
            "detail": "OK",
            "telegram_token": user.telegram_token,
        },
        status=status.HTTP_200_OK,
    )