import uuid

from django.db import models
from django.db.models.fields import BooleanField

from .managers import ConvertMaterialManager, InventoryManager, ItemManager, TaskManager
from .mixins import ConvertTaskMixin, ItemMixin, TaskMixin


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
    inventory_item = models.ForeignKey(
        Inventory, related_name="open_inventory_items", on_delete=models.PROTECT
    )
    remaining = models.FloatField()


class TaskType(models.Model):

    name = models.CharField(
        max_length=32,
    )

    def __str__(self):
        return str(self.name)


class Task(TaskMixin):
    type = models.ForeignKey(TaskType, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, null=True, on_delete=models.PROTECT)
    quantity = models.IntegerField(null=True)

    objects = TaskManager()

    @property
    def latest_status(self):
        return self.task_statuses.last().get_status_display()

    @property
    def transfer_from_location(self):
        return self.transfer_from_locations.last().name


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
    task = models.ForeignKey(
        Task,
        related_name="task_statuses",
        on_delete=models.CASCADE,
    )


class ConsumeTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)


# class SingleOpenInventoryConsume(models.Model):
#     consume_task = models.ForeignKey(ConsumeTask, on_delete=models.CASCADE)
#     single_open_inventory_item = models.ForeignKey(
#         SingleOpenInventory, on_delete=models.PROTECT
#     )


class ConvertTask(ConvertTaskMixin):
    task = models.ForeignKey(
        Task, related_name="convert_task", on_delete=models.CASCADE
    )


class ConvertMaterial(models.Model):
    convert_task = models.ForeignKey(
        ConvertTask, related_name="materials", on_delete=models.CASCADE
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT)

    objects = ConvertMaterialManager()


class ConvertMaterialConsumption(models.Model):
    convert_material = models.ForeignKey(
        ConvertMaterial, related_name="consumption_items", on_delete=models.CASCADE
    )
    inventory_item = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    consume_amount = models.FloatField()
    open_inventory = models.ForeignKey(
        SingleOpenInventory,
        null=True,
        on_delete=models.SET_NULL,
    )
    completely_consumed = models.BooleanField(default=False)


class TransferTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    from_location = models.ForeignKey(
        Location,
        related_name="transfer_from_locations",
        on_delete=models.PROTECT,
    )


# class SingleOpenInventoryTransfer(models.Model):
#     transfer_task = models.ForeignKey(TransferTask, on_delete=models.CASCADE)
#     single_open_inventory_item = models.ForeignKey(
#         SingleOpenInventory, on_delete=models.PROTECT
#     )


class InterfaceTask(models.Model):
    INBOUND = "IN"
    OUTBOUND = "OUT"
    STATUS_TYPES = [
        (INBOUND, "Inbound"),
        (OUTBOUND, "Outbound"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=3,
        choices=STATUS_TYPES,
    )
