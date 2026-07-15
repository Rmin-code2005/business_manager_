from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser
class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email

        return token
    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
        }

        return data
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'phone',
            'email',
            'first_name',
            'last_name',
            'gender',
            'telegram_username',
        )
        

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser

        fields = [
            "email",
            "phone",
            "first_name",
            "last_name",
            "gender",
            "password",
        ]

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        return user
    
class UserTelegramUsernameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['telegram_username']
        
class UserChangeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'email']
        