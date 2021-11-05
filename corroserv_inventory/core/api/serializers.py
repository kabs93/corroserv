from rest_framework import serializers

from corroserv_inventory.core.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


# class ConvertMaterialSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ConvertMaterial
#         fields = "__all__"
