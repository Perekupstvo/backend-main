from django.db import models

from users.models import User


class CarBrand(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Марка")
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="Страна")

    class Meta:
        verbose_name = "Марка"
        verbose_name_plural = "Марки"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(
        CarBrand, on_delete=models.CASCADE, related_name="models", verbose_name="Марка"
    )
    name = models.CharField(max_length=50, verbose_name="Модель")

    class Meta:
        verbose_name = "Модель"
        verbose_name_plural = "Модели"
        unique_together = ("brand", "name")  # Уникальная пара "Марка-Модель"

    def __str__(self):
        return f"{self.name}"


class Vehicle(models.Model):
    FOR_SALE = "for_sale"
    IN_PROGRESS = "in_progress"
    SOLD = "sold"

    STATUS_CHOICES = [
        (FOR_SALE, "В продаже"),
        (IN_PROGRESS, "В работе"),
        (SOLD, "Продан"),
    ]

    # Основные данные
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vehicles", verbose_name="Владелец"
    )
    vin = models.CharField(max_length=17, unique=True, verbose_name="VIN-номер")
    brand = models.ForeignKey(CarBrand, on_delete=models.PROTECT, verbose_name="Марка")
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, verbose_name="Модель")
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    mileage = models.PositiveIntegerField(verbose_name="Пробег")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=FOR_SALE, verbose_name="Статус"
    )
    # Данные о покупке
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость покупки",
        null=True,
        blank=True,
    )
    purchase_date = models.DateField(
        verbose_name="Дата покупки",
        null=True,
        blank=True,
    )
    seller_info = models.TextField(verbose_name="Информация о продавце", null=True, blank=True)
    # Данные о продаже
    sale_price = models.DecimalField(
        verbose_name="Цена продажи", max_digits=10, decimal_places=2, null=True, blank=True
    )
    sale_date = models.DateField(verbose_name="Дата продажи", null=True, blank=True)
    buyer_info = models.TextField(
        verbose_name="Информация о покупателе", null=True, blank=True
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        
    def calculate_benefit(self):
        return (self.sale_price or 0) - (self.purchase_price or 0) - sum(
            expense.amount for expense in self.expenses.all()
        )

    def __str__(self):
        return f"{self.model} ({self.vin})"


class Expense(models.Model):
    REPAID = "repaid"
    DOCUMENTS = "documents"
    DELIVERY = "delivery"
    OTHER = "other"

    EXPENSE_TYPES = [
        (REPAID, "Ремонт"),
        (DOCUMENTS, "Документы"),
        (DELIVERY, "Доставка"),
        (OTHER, "Прочее"),
    ]

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="expenses", verbose_name="Автомобиль"
    )
    expense_type = models.CharField(
        max_length=20, choices=EXPENSE_TYPES, verbose_name="Тип расхода", default=OTHER
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма расхода")
    date = models.DateField(verbose_name="Дата расхода")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    # def __str__(self):
    #     return f"{self.get_expense_type_display()} на {self.vehicle}"
