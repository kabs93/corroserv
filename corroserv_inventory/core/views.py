from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import InboundForm, OutboundForm
from .models import Inventory, Location, Task, TaskStatus, TaskType


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


@login_required
def movement_confirm(
    request: HttpRequest,
    movement_type: str,
    inventory_item_id: int,
) -> HttpResponse:
    (
        item,
        inventory_item,
        inventory_listing,
    ) = Inventory.objects.get_details_for_item(inventory_item_id)

    if movement_type == "Inbound":
        form = InboundForm
    elif movement_type == "Outbound":
        form = OutboundForm
    else:
        form = None
    location_input_error = None

    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            quantity_input = (
                int(form.cleaned_data["quantity"])
                if movement_type == "Inbound"
                else -int(form.cleaned_data["quantity"])
            )
            try:
                location_input = Location.objects.get(
                    name=form.cleaned_data["location"]
                )
                location_input_error = ""
                with transaction.atomic():
                    task_obj = Task.objects.create(
                        item=item,
                        location=location_input,
                        type=TaskType.objects.get(name=movement_type),
                    )
                    TaskStatus.objects.create(task=task_obj, status="CTD")

                    try:
                        inventory_list_item = inventory_listing.get(
                            location=location_input
                        )
                        inventory_list_item.quantity = (
                            inventory_list_item.quantity + quantity_input
                        )
                        inventory_list_item.save()
                    except Inventory.DoesNotExist:
                        if movement_type == "Inbound":
                            Inventory.objects.create(
                                item=item,
                                location=location_input,
                                quantity=quantity_input,
                            )
                        elif movement_type == "Outbound":
                            location_input_error = (
                                "Inventory location does not exist for this item"
                            )
            except Location.DoesNotExist:
                location_input = None
                location_input_error = "Location does not exist"
            print(quantity_input, location_input)
        else:
            print("form.errors")
            print(form.errors)

    context = {
        "movement_type": movement_type,
        "inventory_item_id": inventory_item_id,
        "item": item,
        "inventory_listing": inventory_listing,
        "page_type": "confirm_movement",
        "form": form,
        "location_input_error": location_input_error,
    }

    return render(request, "core/movement_confirm.html", context=context)
