import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .forms import (  # ConvertSelectMaterialsForm,
    ConsumeForm,
    CreateItemForm,
    InboundForm,
    OutboundForm,
)
from .models import Inventory, Item, ItemType
from .serializers import ItemSerializer


@login_required
def home(request: HttpRequest) -> HttpResponse:

    context = {}

    return render(request, "core/home.html", context=context)


@login_required
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
            if item_type == "Product":
                return redirect(
                    "core:convert",
                )
            else:
                return redirect(
                    "core:movement_confirm",
                    movement_type="Inbound",
                    item_uuid=new_item.uuid,
                )

    context = {
        "item_type": item_type,
        "form": form,
    }

    return render(request, "core/create.html", context=context)


@login_required
def task(request: HttpRequest, task_type: str) -> HttpResponse:

    item_type = request.GET.get("item_type", None)

    inventory_listing = Inventory.objects.get_all_by_item_type(item_type)

    context = {
        "task_type": task_type,
        "item_type": item_type,
        "page_type": "select_task",
        "inventory_listing": inventory_listing,
    }

    return render(request, "core/task/task.html", context=context)


@login_required
def task_confirm(
    request: HttpRequest,
    task_type: str,
    item_uuid: uuid,
) -> HttpResponse:

    inventory_item_id = request.GET.get("inventory", None)
    (
        item,
        inventory_item,
        inventory_listing,
    ) = Inventory.objects.get_details_for_item(item_uuid, inventory_item_id)

    form_error = ""

    if request.method == "POST":
        if task_type == "Inbound":
            form = InboundForm(request.POST)
        elif task_type == "Outbound":
            form = OutboundForm(request.POST)
        elif task_type == "Consume":
            form = ConsumeForm(request.POST)

        if form.is_valid():
            form_error = item.create_task_and_update_inventory(
                form_error,
                form,
                task_type,
                item,
                inventory_listing,
            )
            if form_error == "":
                return redirect(request.path_info)
        else:
            print("form.errors")
            print(form.errors)

    else:
        if task_type == "Inbound":
            if inventory_item:
                form = InboundForm(initial={"location": inventory_item.location})
            else:
                form = InboundForm()
        elif task_type == "Outbound":
            if inventory_item:
                form = OutboundForm(initial={"location": inventory_item.location})
            else:
                form = OutboundForm()
        elif task_type == "Consume":
            if inventory_item:
                form = ConsumeForm(initial={"location": inventory_item.location})
            else:
                form = ConsumeForm()
        else:
            form = None

    context = {
        "task_type": task_type,
        "item": item,
        "inventory_item": inventory_item,
        "inventory_listing": inventory_listing,
        "page_type": "confirm_task",
        "form": form,
        "location_input_error": form_error,
    }

    return render(request, "core/task/task_confirm.html", context=context)


@login_required
def convert(request: HttpRequest) -> HttpResponse:

    product_listing = Item.objects.get_all_products()

    context = {
        "product_listing": product_listing,
        "page_type": "select_product",
    }

    return render(request, "core/task/convert.html", context=context)


@login_required
def convert_materials(request: HttpRequest, product_uuid: uuid) -> HttpResponse:

    product = Item.objects.get_product(product_uuid)

    # if request.method == "POST":
    #     form = ConvertSelectMaterialsForm(request.POST)
    #     if form.is_valid():
    #         materials = form.cleaned_data["materials"]
    #         print("materials")
    #         print(materials)
    # else:
    #     form = ConvertSelectMaterialsForm()

    context = {
        "product": product,
        # "form": form,
        "page_type": "select_product_materials",
    }

    return render(request, "core/task/convert_materials.html", context=context)


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.filter(type__name="Material")
    serializer_class = ItemSerializer
