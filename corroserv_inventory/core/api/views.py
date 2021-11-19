import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from corroserv_inventory.core.models import (
    ConvertMaterial,
    ConvertMaterialConsumption,
    Inventory,
    Item,
    Location,
    SingleOpenInventory,
    Task,
)

from .serializers import ItemSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.filter(type__name="Material")
    serializer_class = ItemSerializer


@login_required
@api_view(["POST"])
def confirm_convert_materials(request):

    if request.data:
        product = Item.objects.get(uuid=request.data["product_uuid"])
        selected_materials = [
            Item.objects.get(pk=material["id"])
            for material in request.data["selectedMaterials"]
        ]

    convertTaskId = Task.objects.create_convert_task(
        "Convert", product, selected_materials
    )

    return Response(
        {
            "message": "Added conversion materials",
            "convertTaskId": convertTaskId,
        },
        status=status.HTTP_200_OK,
    )


@login_required
@api_view(["GET", "POST"])
def convert_material_consumption(
    request, convert_material_id: int, location_uuid: uuid
):
    convert_material = ConvertMaterial.objects.get(pk=convert_material_id)
    convert_material_inventory = Inventory.objects.get(
        item=convert_material.item,
        location=Location.objects.get(uuid=location_uuid),
    )

    if request.data:
        consumptionArray = request.data["consumptionArray"]

        with transaction.atomic():
            for item in consumptionArray:

                capacity = convert_material.item.size
                remaining = float(item["quantity"])

                if item["status"] == "Open":

                    open_inventory_item = SingleOpenInventory.objects.get(
                        pk=item["open_inventory_id"]
                    )
                    consumed = open_inventory_item.remaining - remaining

                    if remaining == 0:
                        completely_consumed = True
                        open_inventory_item.delete()
                        convert_material_inventory.quantity -= 1
                        convert_material_inventory.save()

                    else:
                        completely_consumed = False
                        open_inventory_item.remaining = remaining
                        open_inventory_item.save()

                elif item["status"] == "Unopened":
                    consumed = capacity - remaining

                    if remaining == 0:
                        completely_consumed = True
                        convert_material_inventory.quantity -= 1
                        convert_material_inventory.save()

                    else:
                        completely_consumed = False
                        SingleOpenInventory.objects.create(
                            inventory_item=convert_material_inventory,
                            remaining=remaining,
                        )

                else:
                    print("HANDLE ERROR")

                ConvertMaterialConsumption.objects.create(
                    convert_material=convert_material,
                    inventory_item=convert_material_inventory,
                    consume_amount=consumed,
                    completely_consumed=completely_consumed,
                )

        return Response(
            {
                "message": "Added conversion material consumption",
                # "convertTaskId": convertTaskId,
            },
            status=status.HTTP_200_OK,
        )

    else:
        convert_material_inventory_serialized = []

        open_inventory = convert_material_inventory.open_inventory_items.all()
        for opened_item in open_inventory:
            convert_material_inventory_serialized.append(
                {
                    "id": opened_item.inventory_item.id,
                    "name": opened_item.inventory_item.item.name,
                    "location": opened_item.inventory_item.location.name,
                    "status": "Open",
                    "open_inventory_id": opened_item.id,
                    "remaining": opened_item.remaining,
                }
            )
        for unopened_item in range(
            convert_material_inventory.quantity - len(open_inventory)
        ):
            convert_material_inventory_serialized.append(
                {
                    "id": convert_material_inventory.id,
                    "name": convert_material_inventory.item.name,
                    "location": convert_material_inventory.location.name,
                    "status": "Unopened",
                    "open_inventory_id": None,
                    "remaining": f"{convert_material_inventory.item.size}",
                }
            )
        return Response(
            {
                "message": "Material details retrieval success!",
                "convert_material": convert_material_inventory_serialized,
            },
            status=status.HTTP_200_OK,
        )
