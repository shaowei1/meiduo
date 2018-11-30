from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from goods.models import SKU
from goods.search_indexes import SKUIndex


class SKUListSerialziers(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = '__all__'


class SKUSearchSerializers(HaystackSerializer):
    object = SKUListSerialziers()
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')
