import pytest
from rest_framework.test import APIClient

from cars.models import CarBrand, CarModel, Vehicle
from users.models import User


@pytest.fixture
def create_test_user(db):
    """Создаёт тестового пользователя."""
    user = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
    )
    return user


@pytest.fixture
def api_client():
    """Возвращает клиент для API запросов."""
    return APIClient()


@pytest.fixture
def api_client_auth(api_client, create_test_user):
    """Возвращает клиент для API запросов."""
    api_client.force_authenticate(user=create_test_user)
    return api_client


@pytest.fixture
def car_brand(db):
    """Создаёт тестовую марку автомобиля."""
    return CarBrand.objects.create(name="Test Brand")


@pytest.fixture
def car_model(db, car_brand):
    """Создаёт тестовую модель автомобиля."""
    return CarModel.objects.create(brand=car_brand, name="Test Model")

@pytest.fixture
def vehicle(create_test_user, car_brand, car_model):
    return Vehicle.objects.create(
        owner=create_test_user,
        vin="1HGCM82633A123456",
        brand=car_brand,
        model=car_model,
        year=2020,
        mileage=15000,
        purchase_price=1200000.00,
        status="for_sale",
        purchase_date="2024-12-01",
    )

