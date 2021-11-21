import uuid
from typing import Union

from django.db import models, transaction
from django.db.models.query import QuerySet
from django.forms.forms import Form
from django.shortcuts import redirect

import corroserv_inventory.core.models as core_models


class InventoryManager(models.Manager):
    def get_all_by_item_type(
        self,
        type: str,
    ) -> QuerySet["core_models.Inventory"]:

        return self.filter(item__type__name=type, quantity__gt=0)

    def get_details_for_item(
        self,
        item_uuid: uuid,
        inventory_item_id: int = None,
    ) -> Union["core_models.Item", QuerySet["core_models.Inventory"]]:

        item = core_models.Item.objects.get(uuid=item_uuid)

        if inventory_item_id:
            inventory_item = self.get(pk=inventory_item_id)
        else:
            inventory_item = None
        all_inventory_items_for_item = self.filter(item=item, quantity__gt=0)

        return item, inventory_item, all_inventory_items_for_item

    def get_details_for_material(
        self,
        material: "core_models.ConvertMaterial",
    ) -> QuerySet["core_models.Inventory"]:

        return self.filter(
            item=core_models.Item.objects.get(id=material.item.id),
            quantity__gt=0,
        )


class ItemManager(models.Manager):
    def create_item(
        self: "core_models.Item", item_type: str, form: Form
    ) -> "core_models.Item":

        new_item = self.create(
            name=form.cleaned_data["name"],
            type=core_models.ItemType.objects.get(name=item_type),
            uom=form.cleaned_data["uom"],
            size=form.cleaned_data["size"],
        )

        if item_type == "Product":
            return redirect(
                "core:convert",
            )
        else:
            return redirect(
                "core:task_confirm",
                task_type="Inbound",
                item_uuid=new_item.uuid,
            )

    def get_all_products(
        self,
    ) -> QuerySet["core_models.Item"]:

        return self.filter(type__name="Product")

    def get_product(self, product_uuid: uuid) -> "core_models.Item":

        return self.get(uuid=product_uuid)


class TaskManager(models.Manager):
    def get_all_by_task_type(
        self,
        task_type: str,
    ):

        return self.filter(type__name=task_type)
        # if task_type != 'Convert':
        #     return self.filter(type__name=task_type)
        # else:
        #     return self.filter(type__name=task_type)

    def create_convert_task(
        self,
        task_type: str,
        product: "core_models.Item",
        selected_materials: QuerySet["core_models.Item"],
    ) -> int:

        task_type = core_models.TaskType.objects.get(name=task_type)

        with transaction.atomic():

            task = self.create(
                type=task_type,
                item=product,
            )

            core_models.TaskStatus.objects.create(task=task, status="CRT")

            convert_task = core_models.ConvertTask.objects.create(task=task)

            for material in selected_materials:
                core_models.ConvertMaterial.objects.create(
                    convert_task=convert_task,
                    item=material,
                )

        # return redirect("core:convert_task_main", convert_task.id)
        return convert_task.id


class ConvertMaterialManager(models.Manager):
    def get_materials_for_convert_task(
        self,
        convert_task: "core_models.ConvertTask",
    ) -> QuerySet["core_models.ConvertMaterial"]:

        return self.filter(convert_task=convert_task)
