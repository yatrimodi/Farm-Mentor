from django.contrib import admin
from .models import Chat, Expense, SoilMap,FarmerProfile

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    pass

@admin.register(SoilMap)
class SoilMapAdmin(admin.ModelAdmin):
    pass

@admin.register(FarmerProfile)
class SoilMapAdmin(admin.ModelAdmin):
    pass