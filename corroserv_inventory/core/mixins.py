from django.db import models, transaction
from django.db.models.query import QuerySet
from django.forms.forms import Form

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
        quantity_input = (
            int(form.cleaned_data["quantity"])
            if task_type == "Inbound" or task_type == "Convert_Inbound"
            else -int(form.cleaned_data["quantity"])
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
                        type=core_models.TaskType.objects.get(name=task_type),
                    )
                    core_models.TaskStatus.objects.create(task=task_obj, status="CTD")

                try:
                    inventory_list_item = inventory_listing.get(location=location_input)
                    inventory_quantity = inventory_list_item.quantity + quantity_input
                    if inventory_quantity > 0:
                        inventory_list_item.quantity = inventory_quantity
                        inventory_list_item.save()
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

        return form_error

    class Meta:
        abstract = True


class TaskMixin(models.Model):
    def set_complete(self):
        print("self")
        print(self)
        core_models.TaskStatus.objects.create(
            task=self,
            status="CTD",
        )

    class Meta:
        abstract = True
