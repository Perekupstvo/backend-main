import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User


class TestLogin:
    url_login = reverse("token_obtain_pair")
    url_refresh = reverse("token_refresh")

    @pytest.mark.django_db
    def test_token_obtain_with_username(self, api_client, create_test_user):
        """Проверяет, что можно получить токены с логином через username."""
        response = api_client.post(
            self.url_login, {"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    @pytest.mark.django_db
    def test_token_obtain_with_email(self, api_client, create_test_user):
        """Проверяет, что можно получить токены с логином через email."""
        response = api_client.post(
            self.url_login, {"username": "testuser@example.com", "password": "testpassword"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    @pytest.mark.django_db
    def test_token_obtain_invalid_credentials(self, api_client):
        """Проверяет, что при неверных данных токены не выдаются."""
        response = api_client.post(
            self.url_login, {"username": "wronguser", "password": "wrongpassword"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data

    @pytest.mark.django_db
    def test_token_refresh(self, api_client, create_test_user):
        """Проверяет, что можно обновить access токен."""
        # Получаем refresh токен
        response = api_client.post(
            self.url_login, {"username": "testuser", "password": "testpassword"}
        )
        refresh_token = response.data["refresh"]

        # Обновляем токен
        response = api_client.post(self.url_refresh, {"refresh": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


class TestRegistration:
    url_register = "/api/users/auth/register/"

    @pytest.mark.django_db
    def test_registration_success(self, api_client):
        """Проверяет успешную регистрацию пользователя."""
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "patronymic": "Testovich",
        }
        response = api_client.post(self.url_register, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="testuser").exists()

    @pytest.mark.django_db
    def test_registration_password_mismatch(self, api_client):
        """Проверяет ошибку при несовпадении паролей."""
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "confirm_password": "wrongpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = api_client.post(self.url_register, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
