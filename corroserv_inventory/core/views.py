import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import ConsumeForm, CreateItemForm, InboundForm, OutboundForm
from .models import (
    ConvertMaterial,
    ConvertMaterialConsumption,
    ConvertTask,
    Inventory,
    Item,
    Task,
)


@login_required
def home(request: HttpRequest) -> HttpResponse:

    context = {}

    return render(request, "core/home.html", context=context)


@login_required
def view_specific(request: HttpRequest, item_type: str) -> HttpResponse:

    inventory_listing = Inventory.objects.get_all_by_item_type(item_type)

    context = {
        "item_type": item_type,
        "inventory_listing": inventory_listing,
    }

    return render(request, "core/view/view_specific.html", context=context)


@login_required
def create(request: HttpRequest, item_type: str) -> HttpResponseRedirect:

    form = CreateItemForm

    if request.method == "POST":

        form = form(request.POST)

        if form.is_valid():
            return Item.objects.create_item(item_type, form)

    context = {
        "item_type": item_type,
        "form": form,
    }

    return render(request, "core/create.html", context=context)


@login_required
def task(request: HttpRequest, task_type: str) -> HttpResponse:

    task_listing = Task.objects.get_all_by_task_type(task_type)

    context = {
        "task_type": task_type,
        "task_listing": task_listing,
    }

    return render(request, "core/task/task.html", context=context)


@login_required
def task_select_item(request: HttpRequest, task_type: str) -> HttpResponse:

    if task_type == "Convert":
        item_type = "Product"
    else:
        item_type = request.GET.get("item_type", None)

    inventory_listing = Inventory.objects.get_all_by_item_type(item_type)

    context = {
        "task_type": task_type,
        "item_type": item_type,
        "page_type": "select_task",
        "inventory_listing": inventory_listing,
    }

    return render(request, "core/task/task-select-item.html", context=context)


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
            (
                form_error,
                product_location,
                product_quantity,
            ) = item.create_task_and_update_inventory(
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
def task_details(request: HttpRequest, task_id: int) -> HttpResponse:

    task = Task.objects.get(pk=task_id)
    task_type = task.type.name

    if task.latest_status == "Completed":
        print("WOKAY")
        return redirect("core:task", task_type)
    else:
        # Need to Refactor!!!
        print("NOT WOKAY")
        if task_type == "Convert":
            convert_task = ConvertTask.objects.get(task=task)
            return redirect("core:convert_task_main", convert_task.id)
        else:
            return redirect("core:task", task_type)

    # context = {
    #     "task": task,
    # }

    # return render(request, "core/task/task.html", context=context)


@login_required
def convert_select_product(request: HttpRequest) -> HttpResponse:

    product_listing = Item.objects.get_all_products()

    context = {
        "product_listing": product_listing,
        "page_type": "select_product",
    }

    return render(request, "core/task/convert.html", context=context)


@login_required
def convert_materials(request: HttpRequest, product_uuid: uuid) -> HttpResponse:

    product = Item.objects.get(uuid=product_uuid)

    context = {
        "product_uuid": product_uuid,
        "product": product,
        "page_type": "select_product_materials",
    }

    return render(request, "core/task/convert_materials.html", context=context)


@login_required
def convert_task_main(request: HttpRequest, convert_task_id: int) -> HttpResponse:

    convert_task = ConvertTask.objects.get(pk=convert_task_id)
    material_listing = ConvertMaterial.objects.get_materials_for_convert_task(
        convert_task
    )
    consumption_list = ConvertMaterialConsumption.objects.filter(
        convert_material__in=material_listing
    )
    consumption_list_item_ids = [
        item.convert_material.item.id for item in consumption_list
    ]

    conversion_task_error = None

    if request.method == "POST":
        if "delete_convert_task" in request.POST:
            convert_task.task.delete()
            return redirect("core:task", "Convert")
        if "confirm_conversion_task" in request.POST:
            materials_consumption_check = [
                material.item.id in consumption_list_item_ids
                for material in material_listing
            ]

            if False in materials_consumption_check:
                conversion_task_error = "Not all materials have been consumed"
            else:
                return redirect(
                    "core:convert_confirm_product_quantity", convert_task_id
                )

    context = {
        "material_listing": material_listing,
        "convert_task_id": convert_task_id,
        "consumption_list_item_ids": consumption_list_item_ids,
        "conversion_task_error": conversion_task_error,
    }

    return render(request, "core/task/convert_task_main.html", context=context)


@login_required
def convert_material_locations(
    request: HttpRequest,
    convert_task_id: int,
    convert_material_id: int,
) -> HttpResponse:

    material = ConvertMaterial.objects.get(pk=convert_material_id)
    inventory_listing = Inventory.objects.get_details_for_material(material)

    consumption_list = ConvertMaterialConsumption.objects.filter(
        convert_material=material
    )

    consumption_list_inventory_item_ids = [
        item.inventory_item.id for item in consumption_list
    ]

    context = {
        "convert_task_id": convert_task_id,
        "convert_material_id": convert_material_id,
        "material": material,
        "page_type": "select_material",
        "inventory_listing": inventory_listing,
        "consumption_list_inventory_item_ids": consumption_list_inventory_item_ids,
    }

    return render(request, "core/task/convert_material_locations.html", context=context)


@login_required
def convert_material_consumption(
    request: HttpRequest,
    convert_task_id: int,
    convert_material_id: int,
    location_uuid: uuid,
) -> HttpResponse:

    material = ConvertMaterial.objects.get(pk=convert_material_id)

    context = {
        "convert_task_id": convert_task_id,
        "convert_material_id": convert_material_id,
        "location_uuid": location_uuid,
        "material": material,
    }

    return render(
        request, "core/task/convert_material_consumption.html", context=context
    )


@login_required
def convert_confirm_product_quantity(
    request: HttpRequest,
    convert_task_id: int,
) -> HttpResponse:

    convert_task = ConvertTask.objects.get(pk=convert_task_id)
    print("convert_task_id")
    print(convert_task_id)
    product_item = convert_task.task.item
    (
        item,
        inventory_item,
        inventory_listing,
    ) = Inventory.objects.get_details_for_item(product_item.uuid)

    form_error = ""

    task_type = "Convert_Inbound"

    if request.method == "POST":
        form = InboundForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                (
                    form_error,
                    product_location,
                    product_quantity,
                ) = item.create_task_and_update_inventory(
                    form_error,
                    form,
                    task_type,
                    item,
                    inventory_listing,
                )

                if form_error == "":
                    conversion_task_error = (
                        convert_task.confirm_consumption_and_update_inventory()
                    )
                    if not conversion_task_error:
                        parent_task = convert_task.task
                        parent_task.set_complete(product_quantity, product_location)
                        return redirect(
                            "core:task_confirm",
                            task_type="Inbound",
                            item_uuid=product_item.uuid,
                        )
        else:
            print("form.errors")
            print(form.errors)

    else:
        form = InboundForm()

    context = {
        "page_type": "Confirm_Convert",
        "convert_task_id": convert_task_id,
        "form": form,
        "task_type": task_type,
        "item": product_item,
        "inventory_listing": inventory_listing,
    }

    return render(request, "core/task/task_confirm.html", context=context)
