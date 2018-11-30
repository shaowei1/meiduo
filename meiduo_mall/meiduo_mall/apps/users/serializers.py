import re
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers

from goods.models import SKU
from users.models import User
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from celery_tasks.emails.tasks import send_email


class UserSerialzier(serializers.ModelSerializer):
    # 显示指明模型类没有的字段
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)

    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'mobile', 'password2', 'sms_code', 'allow', 'id', 'token')
        # 添加额外参数
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    # 验证手机号格式
    def validate_mobile(self, value):

        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式错误')

        return value

    # 协议的状态判断
    def validate_allow(self, value):

        if value != 'true':
            raise serializers.ValidationError('协议未同意')
        return value

    def validate(self, attrs):

        # 两次密码比对
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证码比对
        # 1、获取redis中真实验证码
        conn = get_redis_connection('sms_code')
        rel_sms_code = conn.get('sms_code_%s' % attrs['mobile'])
        # 2、判断是否超过有效期
        if not rel_sms_code:
            raise serializers.ValidationError('验证码失效')
        # 3、用户输入的验证和真实验证码比对
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):
        # 删除validated_data中的无效数据
        # del validated_data['password2']
        # del validated_data['sms_code']
        # del validated_data['allow']
        # User.objects.create_user(**validated_data)
        # 模型类数据保存
        user = User.objects.create_user(username=validated_data['username'], password=validated_data['password'],
                                        mobile=validated_data['mobile'])

        # jwt加密
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # user添加token
        user.token = token

        return user


class UserDetailSerialzier(serializers.ModelSerializer):
    """
        返回用户信息
    """

    class Meta:
        model = User
        fields = ('username', 'mobile', 'email', 'email_active')


class EmailSeraizlizers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)



    def update(self, instance, validated_data):

        # 更新
        instance.email=validated_data['email']
        instance.save()

        # 加密用户数据
        data={'name':instance.username}
        tjs=TJS(settings.SECRET_KEY,300)
        token=tjs.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token='+token

        # 发送邮件
        # send_mail(subject,'',settings.EMAIL_FROM,[validated_data['email']],html_message=html_message)
        # 异步发送邮件
        send_email.delay(validated_data['email'],verify_url)

        return instance


class SKUHistoriesSerialziers(serializers.Serializer):

    sku_id=serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        # 判断sku——id对应的商品是否存在
        try:
            SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')
        return attrs

    def create(self, validated_data):

        # 1、建立redis连接
        conn=get_redis_connection('history')

        user=self.context['request'].user

        # 2、判纽sku——id是否存储，存储过则删除
        conn.lrem('history_%s'%user.id,0,validated_data['sku_id'])

        # 3、写入sku——id
        conn.lpush('history_%s'%user.id,validated_data['sku_id'])

        # 4、控制列表写入数量
        conn.ltrim('history_%s'%user.id,0,4)

        # 结果返回
        return validated_data





