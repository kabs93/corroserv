from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Inventory


@login_required
def home(request: HttpRequest) -> HttpResponse:

    context = {}

    return render(request, "core/home.html", context=context)


@login_required
def movement(request: HttpRequest, movement_type: str) -> HttpResponse:

    item_type = request.GET.get("item_type", None)

    inventory_listing = Inventory.objects.get_all_by_item_type(item_type)

    print("inventory_listing")
    print(inventory_listing)

    context = {
        "movement_type": movement_type,
        "item_type": item_type,
        "inventory_listing": inventory_listing,
    }

    return render(request, "core/movement.html", context=context)
