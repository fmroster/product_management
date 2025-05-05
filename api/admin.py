from django.contrib import admin
from api.models import Order, OrderItem
from api.models import User
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]

class UserAdmin(admin.ModelAdmin):
    model = User


admin.site.register(Order, OrderAdmin)
admin.site.register(User, UserAdmin)