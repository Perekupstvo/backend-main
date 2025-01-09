from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status as rest_status
from rest_framework.response import Response
from rest_framework.views import APIView

from cars.models import CarBrand, CarModel, Expense, Vehicle

from .serializers import (
    CarBrandModelSerializer,
    CarModelModelSerializer,
    ExpenseSerializer,
    VehicleCreateSerializer,
    VehicleListSerializer,
    VehicleRetrieveSerializer,
    VehicleUpdateSerializer,
    UserStatisticModelSerializer,
)


class VehicleListView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        vehicles = Vehicle.objects.filter(owner=user)

        # Получение параметров фильтрации из запроса
        brand = request.query_params.get("brand", None)
        model = request.query_params.get("model", None)
        status = request.query_params.get("status", None)
        year_from = request.query_params.get("year_from", None)
        year_to = request.query_params.get("year_to", None)
        mileage_from = request.query_params.get("mileage_from", None)
        mileage_to = request.query_params.get("mileage_to", None)
        purchase_price_from = request.query_params.get("purchase_price_from", None)
        purchase_price_to = request.query_params.get("purchase_price_to", None)

        # Применяем фильтры
        if brand:
            vehicles = vehicles.filter(brand__name=brand)
        if model:
            vehicles = vehicles.filter(model__name=model)
        if status:
            vehicles = vehicles.filter(status=status)
        if year_from:
            vehicles = vehicles.filter(year__gte=year_from)
        if year_to:
            vehicles = vehicles.filter(year__lte=year_to)
        if mileage_from:
            vehicles = vehicles.filter(mileage__gte=mileage_from)
        if mileage_to:
            vehicles = vehicles.filter(mileage__lte=mileage_to)
        if purchase_price_from:
            vehicles = vehicles.filter(purchase_price__gte=purchase_price_from)
        if purchase_price_to:
            vehicles = vehicles.filter(purchase_price__lte=purchase_price_to)

        # Сериализация данных
        serializer = VehicleListSerializer(vehicles, many=True)
        return Response(serializer.data, status=rest_status.HTTP_200_OK)


class VehicleCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VehicleCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Указываем владельца как текущего пользователя
            serializer.save(owner=request.user)
            return Response(
                {"detail": "Автомобиль успешно добавлен."}, status=rest_status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=rest_status.HTTP_400_BAD_REQUEST)


class VehicleUpdateView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        try:
            vehicle = Vehicle.objects.get(pk=pk, owner=request.user)
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Автомобиль не найден или вы не являетесь владельцем."},
                status=rest_status.HTTP_404_NOT_FOUND,
            )

        serializer = VehicleUpdateSerializer(vehicle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=rest_status.HTTP_200_OK)

        return Response(serializer.errors, status=rest_status.HTTP_400_BAD_REQUEST)


class VehicleDeleteView(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            # Ищем машину текущего пользователя
            vehicle = Vehicle.objects.get(pk=pk, owner=request.user)
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Автомобиль не найден или вы не являетесь владельцем."},
                status=rest_status.HTTP_404_NOT_FOUND,
            )

        vehicle.delete()
        return Response(
            {"detail": "Автомобиль успешно удалён."}, status=rest_status.HTTP_204_NO_CONTENT
        )


class CarBrandListView(APIView):
    def get(self, request, *args, **kwargs):
        car_brands = CarBrand.objects.all()
        serializer = CarBrandModelSerializer(car_brands, many=True)
        return Response(serializer.data, status=rest_status.HTTP_200_OK)


class CarModelListView(APIView):
    def get(self, request, *args, **kwargs):
        car_models = CarModel.objects.all()
        serializer = CarModelModelSerializer(car_models, many=True)
        return Response(serializer.data, status=rest_status.HTTP_200_OK)


class CarModelRetrieveView(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Модель не найдена."}, status=rest_status.HTTP_404_NOT_FOUND
            )
        serializer = VehicleRetrieveSerializer(vehicle)
        return Response(serializer.data, status=rest_status.HTTP_200_OK)


class ExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        # Получаем все затраты для определенного автомобиля
        vehicle_id = self.kwargs.get("vehicle_id")  # ID автомобиля передается в URL
        return Expense.objects.filter(vehicle_id=vehicle_id).order_by(
            "-date"
        )  # Сортируем по дате (последние в начале)


class ExpenseCreateView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer

    def perform_create(self, serializer):
        vehicle = get_object_or_404(Vehicle, id=self.request.data.get("vehicle"))
        serializer.save(vehicle=vehicle)


class ExpenseDeleteView(generics.DestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def delete(self, request, *args, **kwargs):
        expense = get_object_or_404(Expense, id=kwargs.get("pk"))
        expense.delete()
        return Response(
            {"detail": "Expense deleted successfully."}, status=rest_status.HTTP_204_NO_CONTENT
        )


class UserStatisticView(generics.RetrieveAPIView):
    serializer_class = UserStatisticModelSerializer

    def get_object(self):
        return self.request.user
