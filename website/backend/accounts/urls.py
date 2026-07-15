from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    LoginView,
    RegisterView,
    UserTelegramUsernameUpdateView,
    UserChangeInfoView,
    UserDetailView,
    UserChangeInfoView,
    register_telegram
)
urlpatterns = [
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path("me/",
        UserDetailView.as_view(),
        name="user-detail"),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "update-telegram-username/",
        UserTelegramUsernameUpdateView.as_view(),
        name="update-telegram-username",
    ),
    path(
        "me/change-info/",
        UserChangeInfoView.as_view(),
        name="user-change-info"
    ),
    path(
        "telegram/register/",
        register_telegram,
        name = "telegram-register"
    )
]