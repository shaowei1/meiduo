import re
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser, OAuthSinaUser
from users.models import User


class OauthSerializers(serializers.ModelSerializer):
    # 显示指明模型类没有的字段
    access_token = serializers.CharField(write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    mobile=serializers.CharField(max_length=11)

    class Meta:
        model = User
        fields = ('mobile', 'password', 'access_token', 'sms_code', 'username', 'token', 'user_id')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'read_only': True
            }
        }

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式错误')

        return value

    def validate(self, attrs):

        # 判断access_token
        # 解密
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(attrs['access_token'])  # {'openid':asdasd}
        except:
            raise serializers.ValidationError('无效的access_token')

        # 取出openid
        openid = data.get('openid')
        # attrs 添加openid
        attrs['openid']=openid

        # 验证短信验证码
        # 1、获取redis中真实验证码
        conn = get_redis_connection('sms_code')
        rel_sms_code = conn.get('sms_code_%s' % attrs['mobile'])
        # 2、判断是否超过有效期
        if not rel_sms_code:
            raise serializers.ValidationError('验证码失效')
        # 3、用户输入的验证和真实验证码比对
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        # 判断手机号所对应的用户是否存在
        try:
            user=User.objects.get(mobile=attrs['mobile'])
        except:
            # 用户未注册过
            return attrs

        else:
            # 用户注册过
            # 校验密码
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            attrs['user']=user
            return attrs

    def create(self, validated_data):

        # 判断用户是否注册过
        user=validated_data.get('user',None)

        if user is None:
            # 未注册过
            user=User.objects.create_user(username=validated_data['mobile'],password=validated_data['password'],mobile=validated_data['mobile'])

        # 绑定openid
        OAuthQQUser.objects.create(user=user,openid=validated_data['openid'])

        # jwt加密
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # user添加token
        user.token = token
        user.user_id=user.id
        return user



class SinaSerializers(serializers.ModelSerializer):
    # 显示指明模型类没有的字段
    access_token = serializers.CharField(write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    # image_code = serializers.CharField(max_length=6,min_length=4,write_only=True)
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    mobile=serializers.CharField(max_length=11)

    class Meta:
        model = User
        fields = ('mobile', 'password', 'access_token', 'sms_code','username', 'token', 'user_id')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'read_only': True
            }
        }

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式错误')

        return value

    def validate(self, attrs):

        # 判断access_token
        # 解密
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(attrs['access_token'])  # {'access_token':asdasd}
        except:
            raise serializers.ValidationError('无效的access_token')

        # 取出access_token
        access_token = data.get('access_token')
        # attrs 添加access_token
        attrs['access_token']=access_token

        # 验证短信验证码
        # 1、获取redis中真实验证码
        conn = get_redis_connection('sms_code')
        rel_sms_code = conn.get('sms_code_%s' % attrs['mobile'])
        # 2、判断是否超过有效期
        if not rel_sms_code:
            raise serializers.ValidationError('验证码失效')
        # 3、用户输入的验证和真实验证码比对
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        # 判断手机号所对应的用户是否存在
        try:
            user=User.objects.get(mobile=attrs['mobile'])
        except:
            # 用户未注册过
            return attrs

        else:
            # 用户注册过
            # 校验密码
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            attrs['user']=user
            return attrs

    def create(self, validated_data):

        # 判断用户是否注册过
        user=validated_data.get('user',None)

        if user is None:
            # 未注册过
            user=User.objects.create_user(username=validated_data['mobile'],password=validated_data['password'],mobile=validated_data['mobile'])

        # 绑定access_token
        OAuthSinaUser.objects.create(user=user,access_token=validated_data['access_token'])

        # jwt加密
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # user添加token
        user.token = token
        user.user_id=user.id
        return user
