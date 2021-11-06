import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from corroserv_inventory.core.models import (
    ConvertMaterial,
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

        for item in consumptionArray:
            if item["status"] == "Open":
                print("open consumption")
                with transaction.atomic():
                    ##########################################
                    # Save ConvertMaterialConsumption First
                    ##########################################

                    #####################################################################
                    # Then, update Inventory quantity && SingleOpenInventory Remaining
                    #
                    # ###############################################################
                    # ###############################################################
                    # #### DON'T FORGET TO MINUS INVENTORY QUANTITY IF FULLY CONSUMED
                    # ###############################################################
                    # ###############################################################
                    #
                    #####################################################################
                    open_inventory_item = SingleOpenInventory.objects.get(
                        pk=item["open_inventory_id"]
                    )
                    capacity = open_inventory_item.inventory_item.item.size
                    post_consumption_quantity = float(item["quantity"])
                    remaining = post_consumption_quantity / capacity
                    open_inventory_item.remaining = remaining
                    open_inventory_item.save()

                    #############################################
                    # Only then, update Inventory remaining
                    #############################################

            elif item["status"] == "Unopened":
                print("unopened consumption")
                convert_material_inventory.quantity -= 1
                convert_material_inventory.save()
            else:
                print("HANDLE ERROR")

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
                    "remaining": f"{opened_item.inventory_item.item.size*float(opened_item.remaining)}",
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
