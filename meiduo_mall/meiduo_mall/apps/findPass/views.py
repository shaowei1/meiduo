from random import randint

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.utils import constants
from meiduo_mall.utils.captcha.captcha import captcha
from meiduo_mall.utils.regular import phone_number
from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as TJS


def ImageVerify(request, codeid):
    """
    获取图片验证码
    :return:
    """

    name, text, image = captcha.generate_captcha()
    try:
        # 保存当前生成的图片验证码内容
        conn = get_redis_connection('img_code')

        conn.setex('ImageCode_' + codeid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        return HttpResponse({'message': 'DBERROR'}, content_type='application/json', status=400)
    print(text)
    return HttpResponse(image, content_type="image/png")


def NumberToken(request, username):
    """
    获取手机号和token
    :param request:
    :param phone_number:
    :return: {
            'mobile': mobile,
            'access_token': access_token # 发短信验证的时候不带mobile,所以access_token要包含短息的信息
        }
    """

    text = request.GET.get('text').lower()
    image_code_id = request.GET.get('image_code_id')
    image_code = 'ImageCode_' + image_code_id
    try:
        conn = get_redis_connection('img_code')
        verify = conn.get(image_code).decode().lower()
    except:
        return Response({'message': 'verify is overdue'}, status=400)

    if text == verify:
        try:
            # 4、通过用户名查询数据对象
            if phone_number.match(username):
                # 4、通过用户名查询数据对象
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
            mobile = user.mobile
        except:
            return Response({'message': 'DBERROR'}, status=400)

        # 7、 不存在则进入绑定页面进行保存绑定
        tjs = TJS(settings.SECRET_KEY, 300)
        access_token = tjs.dumps({'mobile': mobile}).decode()
        data = {
            'mobile': mobile,
            'access_token': access_token
        }
        return JsonResponse(data, status=200)
    else:
        return Response({'message': 'verify is error'}, status=400)


class SmsCode(APIView):

    def get(self, request):
        # 1、获取手机号 路由中进行正则匹配
        # 判断请求间隔，是否在60s内
        access_token = request.query_params.get('access_token')

        tjs = TJS(settings.SECRET_KEY, 300)
        mobile = tjs.loads(access_token)['mobile']

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

        # 4. 发送短信
        # send_sms_code.delay(mobile, sms_code)

        # 5、结果返回
        return Response({'message': 'ok'})
        pass


class verifyId(APIView):
    def get(self, request, username):
        sms_code = request.query_params.get('sms_code')

        try:
            user = User.objects.get(username=username)
            mobile = user.mobile
            user_id = user.id
        except:
            return Response({'message': 'DBERROR'}, status=400)

        try:
            conn = get_redis_connection('sms_code')
            sms_verify = conn.get("sms_code_%s" % mobile).decode().lower()
        except:
            return Response({'message': 'verify is overdue'}, status=400)

        # 7、 不存在则进入绑定页面进行保存绑定
        tjs = TJS(settings.SECRET_KEY, 300)
        access_token = tjs.dumps({'user_id': user_id}).decode()

        if sms_code == sms_verify:
            return Response(
                {'user_id': user_id,
                 'access_token': access_token})
        else:
            return Response({'message': 'verify is error'}, status=400)

    pass


class RepairPass(APIView):

    def post(self, request, user_id):
        password = request.data["password"]
        password2 = request.data["password2"]
        access_token = request.data["access_token"]

        if password != password2:
            return Response({'message': 'password is differ'}, status=400)

        tjs = TJS(settings.SECRET_KEY, 300)
        verifyId = tjs.loads(access_token)["user_id"]

        if str(verifyId) != str(user_id):
            return Response({'message': 'DBERROR'}, status=400)
        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
        except:
            return Response({'message': 'DBERROR'}, status=400)

        return Response({'message': 'OK'}, status=200)
