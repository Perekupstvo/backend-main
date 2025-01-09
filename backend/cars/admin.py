from django.contrib import admin

from .models import CarBrand, CarModel, Expense, Vehicle

admin.site.register(CarBrand)
admin.site.register(CarModel)
admin.site.register(Vehicle)
admin.site.register(Expense)
