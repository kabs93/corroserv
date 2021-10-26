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
        inventory_item_id: int,
    ) -> Union[
        "core_models.Item", "core_models.Inventory", QuerySet["core_models.Inventory"]
    ]:
        inventory_item = self.get(pk=inventory_item_id)
        item = core_models.Item.objects.get(pk=inventory_item.item.id)
        all_inventory_items_for_item = self.filter(item=item)

        return item, inventory_item, all_inventory_items_for_item
