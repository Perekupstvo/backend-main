from django.db.models import Count, F, QuerySet, Sum
from rest_framework import serializers

from cars.models import CarBrand, CarModel, Expense, Vehicle, VehiclePhoto
from users.models import User


class VehicleListSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    model = serializers.StringRelatedField()
    expenses_amount = serializers.SerializerMethodField()
    benefit = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "vin",
            "brand",
            "model",
            "year",
            "mileage",
            "purchase_price",
            "sale_price",
            "status",
            "expenses_amount",
            "benefit",
        ]

    def get_expenses_amount(self, obj) -> int:
        expenses_amount = sum(expense.amount for expense in obj.expenses.all())
        return expenses_amount

    def get_benefit(self, obj: Vehicle) -> int:
        return obj.calculate_benefit()


class VehicleCreateSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(
        queryset=CarBrand.objects.all(), write_only=True
    )
    model = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(), write_only=True
    )

    class Meta:
        model = Vehicle
        fields = [
            "vin",
            "brand",
            "model",
            "year",
            "mileage",
            "purchase_price",
            "status",
            "purchase_date",
            "description",
            "seller_info",
            "buyer_info",
        ]

    def validate(self, attrs):
        # Проверяем, что модель относится к указанной марке
        brand = attrs["brand"]
        model = attrs["model"]

        if model.brand != brand:
            raise serializers.ValidationError(
                {"model": "Указанная модель не относится к указанной марке."}
            )

        return attrs

    def create(self, validated_data):
        return Vehicle.objects.create(**validated_data)


class VehicleUpdateSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=CarBrand.objects.all(), required=False)
    model = serializers.PrimaryKeyRelatedField(queryset=CarModel.objects.all(), required=False)

    class Meta:
        model = Vehicle
        fields = [
            "vin",
            "brand",
            "model",
            "year",
            "mileage",
            "purchase_price",
            "status",
            "purchase_date",
            "description",
            "sale_price",
            "sale_date",
            "seller_info",
            "buyer_info",
        ]

    def to_internal_value(self, data):
        # Удаляем поля, значения которых равны None
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return super().to_internal_value(filtered_data)

    def validate(self, attrs):
        # Если указаны brand и model, проверяем их соответствие
        brand = attrs.get("brand")
        model = attrs.get("model")

        if brand and model and model.brand != brand:
            raise serializers.ValidationError(
                {"model": "Указанная модель не относится к указанной марке."}
            )

        return attrs


class CarBrandModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ["id", "name", "country"]


class CarModelModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ["id", "name", "brand"]


class VehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhoto
        fields = ["id", "image"]

    def to_representation(self, instance):
        """Добавляем поле `url` для получения полного URL изображения."""
        representation = super().to_representation(instance)
        representation["url"] = self.context["request"].build_absolute_uri(instance.image.url)
        return representation


class VehicleRetrieveSerializer(serializers.ModelSerializer):
    brand = CarBrandModelSerializer()
    model = CarModelModelSerializer()
    photos = VehiclePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "vin",
            "brand",
            "model",
            "year",
            "mileage",
            "purchase_price",
            "status",
            "purchase_date",
            "sale_price",
            "sale_date",
            "description",
            "seller_info",
            "buyer_info",
            "photos",
        ]


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "vehicle", "expense_type", "amount", "date", "description"]
        read_only_fields = ["id"]


class UserStatisticModelSerializer(serializers.ModelSerializer):
    vehicle_by_status = serializers.SerializerMethodField()
    expenses_by_status = serializers.SerializerMethodField()
    vehicle_count = serializers.SerializerMethodField()
    deals_data = serializers.SerializerMethodField()
    graph_datasets = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "vehicle_by_status",
            "expenses_by_status",
            "vehicle_count",
            "deals_data",
            "graph_datasets",
        ]

    def get_vehicle_by_status(self, obj: User) -> dict:
        """Сколько машин по статусу"""
        data = {}
        for vehicle in obj.vehicles.all().only("status"):
            status = vehicle.status
            data[status] = data.get(status, 0) + 1
        return data

    def get_expenses_by_status(self, obj: User) -> dict:
        """Сколько расходов по статусу"""
        vehicles: QuerySet[Vehicle] = obj.vehicles.all().prefetch_related("expenses")
        data = {}
        for vehicle in vehicles:
            for expense in vehicle.expenses.all():
                status = expense.expense_type
                data[status] = data.get(status, 0) + expense.amount
        return data

    def get_vehicle_count(self, obj: User) -> int:
        """Всего машин"""
        return obj.vehicles.count()

    def get_deals_data(self, obj: User) -> dict:
        """Данные по сделкам"""
        vehicles: QuerySet[Vehicle] = obj.vehicles.all()
        purchased_vehicles = vehicles.filter(purchase_price__isnull=False)
        solded_vehicles = vehicles.filter(sale_price__isnull=False)
        vehicle_benefits_dict = {
            vehicle.id: vehicle.calculate_benefit() for vehicle in vehicles
        }
        data = {
            "purchase_total_amount": sum(
                vehicle.purchase_price for vehicle in purchased_vehicles
            ),
            "sold_total_amount": sum(vehicle.sale_price for vehicle in solded_vehicles),
            "purchase_avg_price": sum(vehicle.purchase_price for vehicle in purchased_vehicles)
            / (purchased_vehicles.count() or 1),
            "sold_avg_price": sum(vehicle.sale_price for vehicle in solded_vehicles)
            / (solded_vehicles.count() or 1),
            "benefit": sum(vehicle.calculate_benefit() for vehicle in vehicles),
            "avg_days_between_purchase_and_sale": (
                sum(
                    (vehicle.sale_date - vehicle.purchase_date).days
                    for vehicle in vehicles.filter(
                        purchase_date__isnull=False, sale_date__isnull=False
                    )
                )
                / vehicles.count()
            ),
            "vehicle_with_benefits": sum(
                1 for vehicle in vehicles if vehicle_benefits_dict[vehicle.id] > 0
            ),
            "vehicle_with_losses": sum(
                1 for vehicle in vehicles if vehicle_benefits_dict[vehicle.id] < 0
            ),
        }
        return data

    def get_graph_datasets(self, obj: User) -> dict:
        """Данные для графиков"""

        def get_count_dataset():
            purchase_data = (
                Vehicle.objects.filter(purchase_date__isnull=False)
                .values("purchase_date")
                .annotate(count=Count("id"), date=F("purchase_date"))
                .order_by("purchase_date")
            )
            sale_data = (
                Vehicle.objects.filter(sale_date__isnull=False)
                .values("sale_date")
                .annotate(count=Count("id"), date=F("sale_date"))
                .order_by("sale_date")
            )
            return {
                "purchase_dates": list(purchase_data),
                "sale_dates": list(sale_data),
            }

        def get_financial_dataset():
            purchase_data = (
                Vehicle.objects.filter(purchase_date__isnull=False)
                .values("purchase_date")
                .annotate(amount=Sum("purchase_price"), date=F("purchase_date"))
                .order_by("purchase_date")
            )
            sale_data = (
                Vehicle.objects.filter(sale_date__isnull=False)
                .values("sale_date")
                .annotate(amount=Sum("sale_price"), date=F("sale_date"))
                .order_by("sale_date")
            )
            return {
                "purchase_dates": list(purchase_data),
                "sale_dates": list(sale_data),
            }

        return {
            "count_dataset": get_count_dataset(),
            "financial_dataset": get_financial_dataset(),
        }
