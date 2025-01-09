import pytest
from django.urls import reverse
from rest_framework import status

from cars.models import Vehicle, Expense


class TestListVehicles:
    url = reverse("vehicle-list")

    @pytest.mark.django_db
    def test_vehicle_list(self, api_client_auth, create_test_user, car_brand, car_model):
        # Создаем несколько тестовых машин
        Vehicle.objects.create(
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
        Vehicle.objects.create(
            owner=create_test_user,
            vin="2HGCM82633A654321",
            brand=car_brand,
            model=car_model,
            year=2019,
            mileage=20000,
            purchase_price=1000000.00,
            status="in_progress",
            purchase_date="2023-11-20",
        )

        # Отправляем GET-запрос
        response = api_client_auth.get(self.url)

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Проверяем количество объектов в ответе
        assert response.data[0]["vin"] == "1HGCM82633A123456"
        assert response.data[1]["vin"] == "2HGCM82633A654321"

    @pytest.mark.django_db
    def test_vehicle_list_empty(self, api_client_auth):
        # Отправляем GET-запрос без созданных машин
        response = api_client_auth.get(self.url)

        # Проверяем успешный ответ с пустым списком
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    @pytest.mark.django_db
    def test_vehicle_list_filtered(
        self, api_client_auth, create_test_user, car_brand, car_model
    ):
        # Создаем несколько тестовых машин
        Vehicle.objects.create(
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
        Vehicle.objects.create(
            owner=create_test_user,
            vin="2HGCM82633A654321",
            brand=car_brand,
            model=car_model,
            year=2019,
            mileage=20000,
            purchase_price=1000000.00,
            status="in_progress",
            purchase_date="2023-11-20",
        )

        # Фильтр по статусу
        response = api_client_auth.get(self.url, {"status": "for_sale"})

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["vin"] == "1HGCM82633A123456"


class TestCreateVehicle:
    url = reverse("vehicle-create")

    @pytest.mark.django_db
    def test_vehicle_creation(self, api_client_auth, car_brand, car_model):
        # Отправляем POST-запрос
        payload = {
            "vin": "1HGCM82633A123456",
            "brand": car_brand.id,
            "model": car_model.id,
            "year": 2020,
            "mileage": 15000,
            "purchase_price": 1200000.00,
            "status": "for_sale",
            "purchase_date": "2024-12-01",
            "description": "Отличное состояние",
        }
        response = api_client_auth.post(self.url, payload)

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert Vehicle.objects.filter(vin="1HGCM82633A123456").exists()


class TestUpdateVehicle:
    @staticmethod
    def url(_id):
        return reverse("vehicle-update", args=[_id])

    @pytest.mark.django_db
    def test_vehicle_update(self, api_client_auth, create_test_user, car_brand, car_model):
        vehicle = Vehicle.objects.create(
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

        # Отправляем PATCH-запрос
        payload = {
            "mileage": 18000,
            "status": "in_progress",
            "description": "Поменяли масло и тормоза",
        }
        print(f"{vehicle.id=}")
        response = api_client_auth.patch(self.url(vehicle.id), payload)

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_200_OK
        vehicle.refresh_from_db()
        assert vehicle.mileage == 18000
        assert vehicle.status == "in_progress"
        assert vehicle.description == "Поменяли масло и тормоза"


class TestDeleteVehicle:
    @staticmethod
    def url(_id):
        return reverse("vehicle-delete", args=[_id])

    @pytest.mark.django_db
    def test_vehicle_delete(self, api_client_auth, create_test_user, car_brand, car_model):
        # Создаём тестовую машину
        vehicle = Vehicle.objects.create(
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

        # Удаляем машину
        response = api_client_auth.delete(self.url(vehicle.id))

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Vehicle.objects.filter(id=vehicle.id).exists()

    @pytest.mark.django_db
    def test_vehicle_delete_not_found(self, api_client_auth, create_test_user):
        # Попытка удалить несуществующую машину
        response = api_client_auth.delete(self.url(999))  # Несуществующий ID
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (
            response.data["detail"] == "Автомобиль не найден или вы не являетесь владельцем."
        )


class TestExpenseList:
    @staticmethod
    def url(vehicle_id):
        return reverse("expense-list", args=[vehicle_id])

    @pytest.mark.django_db
    def test_expense_list(self, api_client_auth, create_test_user, vehicle):
        # Создаём несколько затрат
        Expense.objects.create(
            vehicle=vehicle,
            expense_type="repaid",
            amount=1500.00,
            date="2024-12-01",
            description="Замена масла",
        )
        Expense.objects.create(
            vehicle=vehicle,
            expense_type="documents",
            amount=300.00,
            date="2024-11-01",
            description="Оформление страховки",
        )

        # Отправляем GET-запрос
        response = api_client_auth.get(self.url(vehicle.id))

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["expense_type"] == "repaid"
        assert response.data[0]["amount"] == "1500.00"
        assert response.data[1]["expense_type"] == "documents"
        assert response.data[1]["amount"] == "300.00"

    @pytest.mark.django_db
    def test_expense_list_empty(self, api_client_auth, vehicle):
        # Отправляем GET-запрос
        response = api_client_auth.get(self.url(vehicle.id))

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


class TestExpenseCreate:
    url = reverse("expense-create")

    @pytest.mark.django_db
    def test_expense_create(self, api_client_auth, vehicle):
        # Данные для создания затраты
        payload = {
            "vehicle": vehicle.id,
            "expense_type": "delivery",
            "amount": 500.00,
            "date": "2024-12-02",
            "description": "Доставка новых запчастей",
        }

        # Отправляем POST-запрос
        response = api_client_auth.post(self.url, payload)

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert Expense.objects.filter(vehicle=vehicle, expense_type="delivery").exists()
        expense = Expense.objects.get(vehicle=vehicle, expense_type="delivery")
        assert expense.amount == 500.00
        assert expense.description == "Доставка новых запчастей"

    @pytest.mark.django_db
    def test_expense_create_invalid_vehicle(self, api_client_auth):
        payload = {
            "vehicle": 999,  # Несуществующий ID
            "expense_type": "delivery",
            "amount": 500.00,
            "date": "2024-12-02",
            "description": "Неверный автомобиль",
        }

        response = api_client_auth.post(self.url, payload)

        # Проверяем, что возвращается 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "vehicle" in response.data



class TestExpenseDelete:
    @staticmethod
    def url(expense_id):
        return reverse("expense-delete", args=[expense_id])

    @pytest.mark.django_db
    def test_expense_delete(self, api_client_auth, vehicle):
        # Создаём тестовую затрату
        expense = Expense.objects.create(
            vehicle=vehicle,
            expense_type="documents",
            amount=300.00,
            date="2024-11-01",
            description="Оформление страховки",
        )

        # Удаляем затрату
        response = api_client_auth.delete(self.url(expense.id))

        # Проверяем успешный ответ
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Expense.objects.filter(id=expense.id).exists()

    @pytest.mark.django_db
    def test_expense_delete_not_found(self, api_client_auth):
        response = api_client_auth.delete(self.url(999))  # Несуществующий ID

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "No Expense matches the given query."

