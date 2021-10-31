import uuid

from django.db import models
from django.db.models.fields import BooleanField

from .managers import InventoryManager, ItemManager
from .mixins import ItemMixin


class ItemType(models.Model):

    name = models.CharField(max_length=16)
    asset = BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class UoM(models.Model):

    uom = models.CharField(max_length=2)
    type = models.CharField(max_length=8)

    def __str__(self):
        return str(self.uom)


class Item(ItemMixin):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=64, unique=True)
    type = models.ForeignKey(ItemType, on_delete=models.PROTECT)
    size = models.FloatField(null=True)
    uom = models.ForeignKey(UoM, on_delete=models.PROTECT, null=True)

    objects = ItemManager()

    def __str__(self):
        return str(self.name)


class Location(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return str(self.name)


class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    objects = InventoryManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "location"],
                name="unique_item_location",
            ),
        ]

    def __str__(self):
        return f"{self.location}: {self.item}"


class SingleOpenInventory(models.Model):
    inventory_item = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    remaining = models.DecimalField(max_digits=2, decimal_places=2)


class TaskType(models.Model):

    name = models.CharField(
        max_length=32,
    )

    def __str__(self):
        return str(self.name)


class Task(models.Model):
    type = models.ForeignKey(TaskType, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)


class TaskStatus(models.Model):
    DRAFT = "DRT"
    CREATED = "CRT"
    COMPLETED = "CTD"
    DELETED = "DLT"
    STATUS_TYPES = [
        (DRAFT, "Draft"),
        (CREATED, "Created"),
        (COMPLETED, "Completed"),
        (DELETED, "Deleted"),
    ]

    status = models.CharField(
        max_length=3,
        choices=STATUS_TYPES,
    )
    task = models.ForeignKey(Task, on_delete=models.PROTECT)


class ConsumeTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    quantity = models.IntegerField()


class SingleOpenInventoryConsume(models.Model):
    consume_task = models.ForeignKey(ConsumeTask, on_delete=models.PROTECT)
    single_open_inventory_item = models.ForeignKey(
        SingleOpenInventory, on_delete=models.PROTECT
    )


class ConvertTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)


class ConvertMaterial(models.Model):
    convert_task = models.ForeignKey(ConvertTask, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    consume_quantity = models.DecimalField(max_digits=2, decimal_places=2)


class TransferTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    to_location = models.ForeignKey(Location, on_delete=models.PROTECT)
    quantity = models.IntegerField()


class SingleOpenInventoryTransfer(models.Model):
    transfer_task = models.ForeignKey(TransferTask, on_delete=models.PROTECT)
    single_open_inventory_item = models.ForeignKey(
        SingleOpenInventory, on_delete=models.PROTECT
    )


class InterfaceMovementTask(models.Model):
    INBOUND = "IN"
    OUTBOUND = "OUT"
    STATUS_TYPES = [
        (INBOUND, "Inbound"),
        (OUTBOUND, "Outbound"),
    ]

    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    type = models.CharField(
        max_length=3,
        choices=STATUS_TYPES,
    )
    quantity = models.IntegerField()
