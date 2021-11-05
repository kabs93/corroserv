from django.contrib.auth.decorators import login_required
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from corroserv_inventory.core.models import Item, Task

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
