from django.conf import settings
from django.shortcuts import render
from rest_framework_jwt.views import ObtainJSONWebToken

from goods.models import SKU
from goods.serializers import SKUListSerialziers
from users.models import User
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from random import randint
from django_redis import get_redis_connection
from meiduo_mall.libs.yuntongxun.sms import CCP
from threading import Thread
from celery_tasks.sms_code.tasks import send_sms_code
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
import pickle, base64

# Create your views here.
from users.serializers import UserSerialzier, UserDetailSerialzier, EmailSeraizlizers, SKUHistoriesSerialziers
from users.utils import merge_cart_cookie_to_redis


class SmsCodeView(APIView):
    """
        发送短息
    """

    def get(self, request, mobile):
        # 1、获取手机号 路由中进行正则匹配
        # 判断请求间隔，是否在60s内
        conn = get_redis_connection('sms_code')
        flag = conn.get('sms_code_flag_%s' % mobile)
        if flag:
            return Response({'error': '请求过于频发'}, status=400)

        # 2、生成短信验证
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        # 3、保存短信到redis缓存
        pl = conn.pipeline()  # 生成管道对象
        pl.setex('sms_code_%s' % mobile, 300, sms_code)
        pl.setex('sms_code_flag_%s' % mobile, 60, 'a')
        pl.execute()
        # 4、发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, '5'], 1)
        # 异步发送短信
        # t=Thread(target='send_sms_code',kwargs={'mobile':mobile,'sms_code':sms_code})
        # t.start()

        # send_sms_code.delay(mobile, sms_code)

        # 5、结果返回
        return Response({'message': 'ok'})


class UserNameView(APIView):
    """
        判断用户名号
    """

    def get(self, request, username):
        # 1、获取name值，正则匹配
        # 2、查询数据库中name所对应数据对象的数量
        count = User.objects.filter(username=username).count()
        # 3、返回对象数量
        return Response(
            {
                'count': count
            }
        )


class MobileView(APIView):
    """
        判断手机号
    """

    def get(self, request, mobile):
        # 1、获取mobile值，正则匹配
        # 2、查询数据库中mobile所对应数据对象的数量
        count = User.objects.filter(mobile=mobile).count()
        # 3、返回对象数量
        return Response(
            {
                'count': count
            }
        )


class UsersView(CreateAPIView):
    """
        注册保存用户数据
    """
    serializer_class = UserSerialzier


class UserDetailView(RetrieveAPIView):
    """
        获取用户信息
    """
    serializer_class = UserDetailSerialzier
    permission_classes = [IsAuthenticated]

    # 重写方法，按照指定对象返回
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """
        更新邮箱
    """
    serializer_class = EmailSeraizlizers

    # 重写方法，按照指定对象返回
    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    """
        验证邮箱
    """

    def get(self, request):
        # 1、获取前端数据
        token = request.query_params.get('token', None)
        if token is None:
            return Response({'errors': '缺少token'}, status=400)
        # 2、验证数据。 解密token。{‘name’:python}
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(token)
        except:
            return Response({'errors': '无效token'}, status=400)
        # 3、获取用户名
        username = data['name']
        # 4、通过用户名查询数据对象
        user = User.objects.get(username=username)
        # 5、更新邮箱验证状态
        user.email_active = True
        user.save()
        # 6、返回结果
        return Response({
            'message': 'ok'
        })


class SKUHistoriesView(CreateAPIView):
    """
        保存用户浏览历史记录
    """
    serializer_class = SKUHistoriesSerialziers

    def get(self, request):
        # 1、获取用户对象
        user = request.user
        # 2、查询redis中sku——id
        conn = get_redis_connection('history')
        sku_ids = conn.lrange('history_%s' % user.id, 0, 6)
        # 3、通过sku——id查询数据对象
        skus = SKU.objects.filter(id__in=sku_ids)
        # 4、序列化返回
        ser = SKUListSerialziers(skus, many=True)
        return Response(ser.data)


class UserLoginView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            # 合并购物车
            response = merge_cart_cookie_to_redis(request, response, user)

        return response
