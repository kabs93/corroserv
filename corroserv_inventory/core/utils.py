from django.db.models.query import QuerySet
from django.forms.forms import Form
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect

import corroserv_inventory.core.models as core_models

from .forms import ConsumeForm, InboundForm, OutboundForm, TransferForm


def getFormByTaskType(
    task_type: str,
    inventory_item: "core_models.Inventory",
) -> Form:

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
    elif task_type == "Transfer":
        if inventory_item:
            form = TransferForm(initial={"from_location": inventory_item.location})
        else:
            form = TransferForm()
    else:
        form = None

    return form


def processFormByTaskType(
    request: HttpRequest,
    task_type: str,
    item: "core_models.Item",
    inventory_listing: QuerySet["core_models.Inventory"],
):

    form_error = ""

    if task_type == "Inbound" or task_type == "Convert_Inbound":
        form = InboundForm(request.POST)
    elif task_type == "Outbound":
        form = OutboundForm(request.POST)
    elif task_type == "Consume":
        form = ConsumeForm(request.POST)
    elif task_type == "Transfer":
        form = TransferForm(request.POST)

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
    return form_error, product_location, product_quantity


def formSuccessRedirectByTaskType(
    request: HttpRequest,
    task_type: str,
    product_quantity: int = None,
    product_location: "core_models.Location" = None,
    convert_task: "core_models.ConvertTask" = None,
    product_item: "core_models.Item" = None,
) -> HttpResponseRedirect:

    if task_type == "Transfer":
        return redirect("core:task", task_type)

    elif task_type == "Convert_Inbound":

        conversion_task_error = convert_task.confirm_consumption_and_update_inventory()

        if not conversion_task_error:

            parent_task = convert_task.task
            parent_task.set_complete(product_quantity, product_location)

            return redirect(
                "core:task_confirm",
                task_type="Inbound",
                item_uuid=product_item.uuid,
            )

    else:
        return redirect(request.path_info)
