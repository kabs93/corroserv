import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import CreateItemForm, InboundForm
from .models import ConvertMaterial, ConvertTask, Inventory, Item, Task
from .utils import (
    formSuccessRedirectByTaskType,
    getFormByTaskType,
    processFormByTaskType,
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
        form_error, _, _ = processFormByTaskType(
            request, task_type, item, inventory_listing
        )

        if form_error == "":
            success_redirect = formSuccessRedirectByTaskType(request, task_type)
            return success_redirect

    else:
        form = getFormByTaskType(task_type, inventory_item)

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

    (
        material_listing,
        consumption_list_item_ids,
    ) = convert_task.get_materials_and_consumption_item_ids()

    conversion_task_error = None

    if request.method == "POST":
        if "delete_convert_task" in request.POST:
            return convert_task.delete_and_redirect()
        if "confirm_conversion_task" in request.POST:
            (
                success_redirect,
                conversion_task_error,
            ) = convert_task.check_materials_consumption(
                material_listing, consumption_list_item_ids, convert_task_id
            )
            if success_redirect:
                return success_redirect

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

    (
        inventory_listing,
        consumption_list_inventory_item_ids,
    ) = material.get_material_inventory_and_consumption_inventory_ids()

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
    product_item = convert_task.task.item
    (
        item,
        inventory_item,
        inventory_listing,
    ) = Inventory.objects.get_details_for_item(product_item.uuid)

    task_type = "Convert_Inbound"

    if request.method == "POST":
        with transaction.atomic():

            form_error, product_location, product_quantity = processFormByTaskType(
                request, task_type, item, inventory_listing
            )

            if form_error == "":
                success_redirect = formSuccessRedirectByTaskType(
                    request,
                    task_type,
                    product_quantity,
                    product_location,
                    convert_task,
                    product_item,
                )
                return success_redirect

            else:
                print("form_error")
                print(form_error)

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
