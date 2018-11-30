from rest_framework import serializers

from goods.models import SKU


class CartsSerialziers(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')

        # 判断库存
        if attrs['count'] > sku.stock:
            raise serializers.ValidationError('商品库存不足')

        return attrs

class CartsListSerialzier(serializers.ModelSerializer):
    count = serializers.IntegerField(min_value=1,read_only=True)
    selected = serializers.BooleanField(default=True,read_only=True)

    class Meta:
        model=SKU
        fields="__all__"

class CartsDeleteSerialziers(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')

        return attrs

class CartsSelectedSerialziers(serializers.Serializer):

    selected = serializers.BooleanField(default=True)



