import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import CreateItemForm, InboundForm, OutboundForm
from .models import Inventory, Item, ItemType


@login_required
def home(request: HttpRequest) -> HttpResponse:

    context = {}

    return render(request, "core/home.html", context=context)


@login_required
def movement(request: HttpRequest, movement_type: str) -> HttpResponse:

    item_type = request.GET.get("item_type", None)

    inventory_listing = Inventory.objects.get_all_by_item_type(item_type)

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
    item_uuid: uuid,
    inventory_item_id: int = None,
) -> HttpResponse:
    (
        item,
        inventory_item,
        inventory_listing,
    ) = Inventory.objects.get_details_for_item(item_uuid, inventory_item_id)

    location_input_error = ""

    if movement_type == "Inbound":
        if inventory_item:
            form = InboundForm(initial={"location": inventory_item.location})
        else:
            form = InboundForm
    elif movement_type == "Outbound":
        form = OutboundForm(initial={"location": inventory_item.location})
    else:
        form = None

    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            location_input_error = item.create_movement_task_and_update_inventory(
                location_input_error,
                form,
                movement_type,
                item,
                inventory_listing,
            )
            if location_input_error == "":
                return redirect(request.path_info)
        else:
            print("form.errors")
            print(form.errors)

    context = {
        "movement_type": movement_type,
        "item": item,
        "inventory_item": inventory_item,
        "inventory_listing": inventory_listing,
        "page_type": "confirm_movement",
        "form": form,
        "location_input_error": location_input_error,
    }

    return render(request, "core/movement_confirm.html", context=context)


def create(request: HttpRequest, item_type: str) -> HttpResponse:

    form = CreateItemForm

    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            new_item = Item.objects.create(
                name=form.cleaned_data["name"],
                type=ItemType.objects.get(name=item_type),
                uom=form.cleaned_data["uom"],
                size=form.cleaned_data["size"],
            )
            return redirect(
                "core:movement_confirm",
                movement_type="Inbound",
                item_uuid=new_item.uuid,
                inventory_item_id=None,
            )

    context = {
        "item_type": item_type,
        "form": form,
    }

    return render(request, "core/create.html", context=context)
