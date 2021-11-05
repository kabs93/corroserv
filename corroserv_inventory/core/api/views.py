from django.contrib.auth.decorators import login_required
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from corroserv_inventory.core.models import ConvertMaterial, Inventory, Item, Task

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

    # return redirect_to_convert_task_main

    return Response(
        {
            "message": "Added conversion materials",
            "convertTaskId": convertTaskId,
        },
        status=status.HTTP_200_OK,
    )


@login_required
@api_view(["GET", "POST"])
def convert_material_consumption(request, convert_material_id: int):

    convert_material_inventory_serialized = []

    convert_material = ConvertMaterial.objects.get(pk=convert_material_id)
    convert_material_inventory = Inventory.objects.filter(item=convert_material.item)

    for inventory_item in convert_material_inventory:
        open_inventory = inventory_item.open_inventory_items.all()
        convert_material_inventory_serialized.append(
            {
                "id": inventory_item.id,
                "name": inventory_item.item.name,
                "location": inventory_item.location.name,
                "quantity": inventory_item.quantity - len(open_inventory),
                "status": "Unopened",
                "remaining": f"{inventory_item.item.size}",
            }
        )
        for item in open_inventory:
            convert_material_inventory_serialized.append(
                {
                    "id": item.inventory_item.id,
                    "name": item.inventory_item.item.name,
                    "location": item.inventory_item.location.name,
                    "quantity": 1,
                    "status": "Open",
                    "remaining": f"{item.inventory_item.item.size*float(item.remaining)}",
                }
            )

    return Response(
        {
            "message": "Material details retrieval success!",
            "convert_material": convert_material_inventory_serialized,
        },
        status=status.HTTP_200_OK,
    )
