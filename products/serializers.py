# serializers.py
from rest_framework import serializers

class GenerateQRInputSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    select_all = serializers.BooleanField(default=False)
    include_barcode = serializers.BooleanField(default=False)
    domain = serializers.CharField()
