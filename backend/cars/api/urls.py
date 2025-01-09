from django.urls import path

from .views import (
    CarBrandListView,
    CarModelListView,
    CarModelRetrieveView,
    ExpenseCreateView,
    ExpenseDeleteView,
    ExpenseListView,
    VehicleCreateView,
    VehicleDeleteView,
    VehicleListView,
    VehicleUpdateView,
    UserStatisticView,
)

VEHICLE = "vehicles/"
BRANDS = "brands/"
MODELS = "models/"
EXPENSES = "expenses/"

urlpatterns = [
    path(VEHICLE + "list/", VehicleListView.as_view(), name="vehicle-list"),
    path(
        VEHICLE + "retrieve/<int:pk>/", CarModelRetrieveView.as_view(), name="vehicle-retrieve"
    ),
    path(VEHICLE + "create/", VehicleCreateView.as_view(), name="vehicle-create"),
    path(VEHICLE + "update/<int:pk>/", VehicleUpdateView.as_view(), name="vehicle-update"),
    path(VEHICLE + "delete/<int:pk>/", VehicleDeleteView.as_view(), name="vehicle-delete"),
    path(BRANDS + "list/", CarBrandListView.as_view(), name="car-brand-list"),
    path(MODELS + "list/", CarModelListView.as_view(), name="car-model-list"),
    path(EXPENSES + "list/<int:vehicle_id>/", ExpenseListView.as_view(), name="expense-list"),
    path(EXPENSES + "create/", ExpenseCreateView.as_view(), name="expense-create"),
    path(EXPENSES + "delete/<int:pk>/", ExpenseDeleteView.as_view(), name="expense-delete"),
    path("statistic/", UserStatisticView.as_view(), name="user-statistic"),
]
