import uuid
from typing import Union

from django.db import models
from django.db.models.query import QuerySet

import corroserv_inventory.core.models as core_models


class InventoryManager(models.Manager):
    def get_all_by_item_type(
        self,
        type: str,
    ) -> QuerySet["core_models.Inventory"]:

        return self.filter(item__type__name=type)

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
