from rest_framework import serializers

from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "photo",
        ]  # Поля, которые можно редактировать
        read_only_fields = ["id", "username"]  # Эти поля нельзя редактировать
