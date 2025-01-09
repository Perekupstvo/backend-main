import bcrypt
from django.contrib.auth.models import BaseUserManager
from django.db import models

from common.models import BaseUserModel


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        if not username:
            raise ValueError("Username обязателен")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser должен иметь is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser должен иметь is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


def user_photo_path(instance, filename):
    return f"photos/user/{instance.pk}/profile/{filename}"


class User(BaseUserModel):
    """Кастомная модель пользователя"""

    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    patronymic = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Храним хэшированный пароль
    photo = models.ImageField(
        upload_to=user_photo_path,  # Путь для загрузки изображений
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def set_password(self, raw_password):
        self.password = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode(), self.password.encode())

    def __str__(self):
        return self.username
