from django.shortcuts import render
from django.db.models import Sum, F

from .models import User, Product, Cart


def analytics_dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_cart_items = Cart.objects.count()

    total_stock = (
        Product.objects.aggregate(
            total=Sum("stock")
        )["total"] or 0
    )

    total_cart_quantity = (
        Cart.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    inventory_value = (
        Product.objects.aggregate(
            total=Sum(F("price") * F("stock"))
        )["total"] or 0
    )

    context = {
        "total_users": total_users,
        "total_products": total_products,
        "total_cart_items": total_cart_items,
        "total_stock": total_stock,
        "total_cart_quantity": total_cart_quantity,
        "inventory_value": inventory_value,
    }

    return render(
        request,
        "analytics/dashboard.html",
        context
    )