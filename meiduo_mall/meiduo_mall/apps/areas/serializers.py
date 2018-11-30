import re
from rest_framework import serializers

from areas.models import Area
from users.models import Address


class AreasSerializers(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class AddressSerializers(serializers.ModelSerializer):
    city_id = serializers.IntegerField(write_only=True)
    district_id = serializers.IntegerField(write_only=True)
    province_id = serializers.IntegerField(write_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude = ('user',)

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式错误')

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        # validated_data添加用户数据
        validated_data['user'] = user

        address = super().create(validated_data)

        return address
