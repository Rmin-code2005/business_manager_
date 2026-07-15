from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .managers import CustomUserManager
from .validators import validate_iran_phone , validate_telegram_username


class CustomUser(AbstractUser):

    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
    telegram_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        db_index=True
    )
    username = None
    telegram_username = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_telegram_username],
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )

    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_iran_phone],
    )

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "phone",
        "first_name",
        "last_name",
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"])

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=["is_active", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)