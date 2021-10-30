from django.db import models, transaction
from django.db.models.query import QuerySet
from django.forms.forms import Form

import corroserv_inventory.core.models as core_models


class ItemMixin(models.Model):
    def create_movement_task_and_update_inventory(
        self,
        location_input_error: str,
        form: Form,
        movement_type: str,
        item: "core_models.Item",
        inventory_listing: QuerySet["core_models.Inventory"],
    ):
        quantity_input = (
            int(form.cleaned_data["quantity"])
            if movement_type == "Inbound"
            else -int(form.cleaned_data["quantity"])
        )
        try:
            location_input = core_models.Location.objects.get(
                name=form.cleaned_data["location"]
            )
            with transaction.atomic():
                task_obj = core_models.Task.objects.create(
                    item=item,
                    location=location_input,
                    type=core_models.TaskType.objects.get(name=movement_type),
                )
                core_models.TaskStatus.objects.create(task=task_obj, status="CTD")

                try:
                    inventory_list_item = inventory_listing.get(location=location_input)
                    inventory_list_item.quantity = (
                        inventory_list_item.quantity + quantity_input
                    )
                    inventory_list_item.save()
                except core_models.Inventory.DoesNotExist:
                    if movement_type == "Inbound":
                        core_models.Inventory.objects.create(
                            item=item,
                            location=location_input,
                            quantity=quantity_input,
                        )
                    elif movement_type == "Outbound":
                        location_input_error = (
                            "Inventory location does not exist for this item"
                        )

        except core_models.Location.DoesNotExist:
            # location_input = None
            location_input_error = "Location does not exist"

        return location_input_error

    class Meta:
        abstract = True
