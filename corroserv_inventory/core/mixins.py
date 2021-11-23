from typing import List, Tuple, Union

from django.db import models, transaction
from django.db.models.query import QuerySet
from django.forms.forms import Form
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect

import corroserv_inventory.core.models as core_models


class ItemMixin(models.Model):
    def create_task_and_update_inventory(
        self,
        form_error: str,
        form: Form,
        task_type: str,
        item: "core_models.Item",
        inventory_listing: QuerySet["core_models.Inventory"],
    ):
        interface_task_type = {
            "Inbound": "IN",
            "Outbound": "OUT",
        }

        quantity_input = (
            -int(form.cleaned_data["quantity"])
            if task_type in ["Outbound", "Consume"]
            else int(form.cleaned_data["quantity"])
        )
        try:
            location_input = core_models.Location.objects.get(
                name=form.cleaned_data["location"]
            )
            with transaction.atomic():
                if task_type != "Convert_Inbound":
                    task_obj = core_models.Task.objects.create(
                        item=item,
                        location=location_input,
                        quantity=quantity_input,
                        type=core_models.TaskType.objects.get(name=task_type),
                    )
                    if task_type == "Transfer":
                        core_models.TransferTask.objects.create(
                            task=task_obj,
                            from_location=core_models.Location.objects.get(
                                name=form.cleaned_data["from_location"]
                            ),
                        )
                    elif task_type == "Consume":
                        core_models.ConsumeTask.objects.create(
                            task=task_obj,
                        )
                    else:
                        core_models.InterfaceTask.objects.create(
                            task=task_obj,
                            type=interface_task_type[task_type],
                        )
                    core_models.TaskStatus.objects.create(task=task_obj, status="CTD")

                try:
                    inventory_list_item = inventory_listing.get(location=location_input)
                    if task_type == "Transfer":
                        from_inventory_list_item = inventory_listing.get(
                            location=core_models.Location.objects.get(
                                name=form.cleaned_data["from_location"]
                            )
                        )
                    inventory_quantity = inventory_list_item.quantity + quantity_input
                    if inventory_quantity > 0:
                        inventory_list_item.quantity = inventory_quantity
                        inventory_list_item.save()
                        if task_type == "Transfer":
                            from_inventory_list_item.quantity = (
                                from_inventory_list_item.quantity - quantity_input
                            )
                            from_inventory_list_item.save()

                    else:
                        form_error = "Input quantity is higher than the quantity available in this location"
                except core_models.Inventory.DoesNotExist:
                    if task_type == "Inbound" or task_type == "Convert_Inbound":
                        core_models.Inventory.objects.create(
                            item=item,
                            location=location_input,
                            quantity=quantity_input,
                        )
                    else:
                        form_error = "Inventory location does not exist for this item"

        except core_models.Location.DoesNotExist:
            # location_input = None
            form_error = "Location does not exist"

        return (
            form_error,
            location_input,
            quantity_input,
        )

    class Meta:
        abstract = True


class TaskMixin(models.Model):
    def set_complete(
        self,
        product_quantity: int,
        product_location: "core_models.Location",
    ) -> None:

        # Update Quantity and Location in Task table
        self.quantity = product_quantity
        self.location = product_location
        self.save()

        # Update TaskStatus to CTD
        core_models.TaskStatus.objects.create(
            task=self,
            status="CTD",
        )

    class Meta:
        abstract = True


class ConvertTaskMixin(models.Model):
    def get_materials_and_consumption_item_ids(
        self: "core_models.ConvertTask",
    ) -> Tuple[QuerySet["core_models.ConvertMaterial"], List[int]]:

        # Get Materials

        materials = core_models.ConvertMaterial.objects.get_materials_for_convert_task(
            self
        )

        # Get Consumption Item Ids

        consumption_list = core_models.ConvertMaterialConsumption.objects.filter(
            convert_material__in=materials
        )

        consumption_item_ids = [
            item.convert_material.item.id for item in consumption_list
        ]

        return materials, consumption_item_ids

    def delete_and_redirect(self) -> HttpResponseRedirect:

        self.task.delete()
        return redirect("core:task", "Convert")

    def check_materials_consumption(
        self: "core_models.ConvertTask",
        material_listing: QuerySet["core_models.ConvertMaterial"],
        consumption_list_item_ids: List[int],
        convert_task_id: int,
    ) -> Union[HttpResponseRedirect, str]:

        conversion_task_error = None
        success_redirect = None

        materials_consumption_check = [
            material.item.id in consumption_list_item_ids
            for material in material_listing
        ]

        if False in materials_consumption_check:
            conversion_task_error = "Not all materials have been consumed"
        else:
            success_redirect = redirect(
                "core:convert_confirm_product_quantity", convert_task_id
            )

        return success_redirect, conversion_task_error

    def confirm_consumption_and_update_inventory(
        self: "core_models.ConvertTask",
    ) -> str:

        conversion_task_error = None

        materials = self.materials.all()

        with transaction.atomic():
            for material in materials:
                for consumption_item in material.consumption_items.all():

                    consumption_amount = consumption_item.consume_amount
                    material_inventory = consumption_item.inventory_item

                    if consumption_item.open_inventory_id:
                        print("consumption_item.open_inventory_id")
                        print(consumption_item.open_inventory_id)
                        open_inventory_item = (
                            core_models.SingleOpenInventory.objects.get(
                                pk=consumption_item.open_inventory_id
                            )
                        )
                        if consumption_item.completely_consumed:
                            open_inventory_item.delete()
                            material_inventory.quantity -= 1
                            material_inventory.save()
                        else:
                            open_inventory_item.remaining = (
                                open_inventory_item.remaining - consumption_amount
                            )
                            open_inventory_item.save()
                    else:
                        if consumption_item.completely_consumed:
                            material_inventory.quantity -= 1
                            material_inventory.save()
                        else:
                            core_models.SingleOpenInventory.objects.create(
                                inventory_item=material_inventory,
                                remaining=material.item.size - consumption_amount,
                            )

        return conversion_task_error

    class Meta:
        abstract = True


class ConvertMaterialMixin(models.Model):
    def get_material_inventory_and_consumption_inventory_ids(
        self: "core_models.ConvertMaterial",
    ) -> Tuple[QuerySet["core_models.Inventory"], List[int]]:

        # Get Inventory List

        inventory_list = core_models.Inventory.objects.get_details_for_material(self)

        # Get Consumption List Inventory Item Ids

        consumption_list = core_models.ConvertMaterialConsumption.objects.filter(
            convert_material=self
        )

        consumption_inventory_ids = [
            item.inventory_item.id for item in consumption_list
        ]

        return inventory_list, consumption_inventory_ids

    class Meta:
        abstract = True
