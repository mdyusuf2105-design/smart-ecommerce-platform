from django.contrib import admin

from .models import User, Product, Cart


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "role",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
    )

    list_filter = (
        "role",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "stock",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "product_id",
        "quantity",
    )