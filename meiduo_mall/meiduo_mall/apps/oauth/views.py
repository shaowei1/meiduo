from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from QQLoginTool.QQtool import OAuthQQ
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from rest_framework.generics import CreateAPIView

# Create your views here.
from rest_framework_jwt.settings import api_settings

from meiduo_mall.utils.captcha.captcha import captcha
from oauth.models import OAuthQQUser, OAuthSinaUser
from oauth.serializers import OauthSerializers, SinaSerializers
from oauth.sina_oauth import OAuthSina
from users.utils import merge_cart_cookie_to_redis


class OauthLoginView(APIView):
    """
        构建qq登录的跳转链接
    """

    def get(self, request):
        # 1、获取前端  state
        state = request.query_params.get('next', None)
        # 2、前端没有传递state，需要手动指定
        if state is None:
            state = '/'
        # 3、初始化OAuthQQ对象
        qq = OAuthQQ(client_secret=settings.QQ_CLIENT_SECRET, client_id=settings.QQ_CLIENT_ID,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        # 4、构建qq登录页面的跳转连接
        login_url = qq.get_qq_url()
        # 5、返回结果
        return Response({'login_url': login_url})


class OauthView(CreateAPIView):
    """
        获取openeid和绑定openid
    """
    serializer_class = OauthSerializers

    def get(self, request):
        # 1、获取code值
        code = request.query_params.get('code', None)
        # 2、判断是否真的前端传递有code值
        if code is None:
            return Response({'errors': '缺少code值'}, status=400)
        # 3、通过code值获取access_token
        # 初始化OAuthQQ对象
        qq = OAuthQQ(client_secret=settings.QQ_CLIENT_SECRET, client_id=settings.QQ_CLIENT_ID,
                     redirect_uri=settings.QQ_REDIRECT_URI, state='/')
        access_token = qq.get_access_token(code)

        # 4、通过access_token值
        openid = qq.get_open_id(access_token)

        # 5、判断openid是否绑定
        try:
            # 6、查询openid所对应的数据是否存在
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except:

            # 7、 不存在则进入绑定页面进行保存绑定
            tjs=TJS(settings.SECRET_KEY,300)
            open_id=tjs.dumps({'openid':openid}).decode()
            return Response({'access_token':open_id})
        else:
            # 8、存在则用户登录成功跳转到首页
            # 9、生成jwt token值
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response=Response(
                {
                    'token': token,
                    'username': user.username,
                    'user_id': user.id
                }
            )
            response=merge_cart_cookie_to_redis(request,response,user)

            return response



# 构建weibo登录的跳转链接
class SinaLoginView(APIView):
    """
        构建weibo登录的跳转链接
    """

    def get(self, request):
        # 1、获取前端  state
        state = request.query_params.get('next', None)
        # 2、前端没有传递state，需要手动指定
        if state is None:
            state = '/'
        # 3、初始化OAuthQQ对象
        sina = OAuthSina(client_secret=settings.SINA_CLIENT_SECRET, client_id=settings.SINA_CLIENT_ID,
                     redirect_uri=settings.SINA_REDIRECT_URI, state=state)
        # 4、构建qq登录页面的跳转连接
        login_url = sina.get_sina_url()
        # 5、返回结果
        return Response({'login_url': login_url})

# 获取access_token和绑定access_token
class SinaView(CreateAPIView):
    serializer_class = SinaSerializers


    def get(self, request, *args, **kwargs):
        # 1、获取code值
        code = request.query_params.get('code', None)
        # 2、判断是否真的前端传递有code值
        if code is None:
            return Response({'errors': '缺少code值'}, status=400)
            # 3、通过code值获取access_token
            # 初始化OAuthSina对象
        sina = OAuthSina(client_secret=settings.SINA_CLIENT_SECRET, client_id=settings.SINA_CLIENT_ID,
                     redirect_uri=settings.SINA_REDIRECT_URI, state='/')
        access_token = sina.get_access_token(code)['access_token']
        # 5、判断access_token是否绑定
        try:
            # 6、查询access_token所对应的数据是否存在
            sina_user = OAuthSinaUser.objects.get(access_token=access_token)
        except:

            # 7、 不存在则进入绑定页面进行保存绑定
            tjs = TJS(settings.SECRET_KEY, 300)
            access_token = tjs.dumps({'access_token': access_token}).decode()
            return Response({'access_token': access_token})
        else:
            # 8、存在则用户登录成功跳转到首页
            # 9、生成jwt token值
            user = sina_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response(
                {
                    'token': token,
                    'username': user.username,
                    'user_id': user.id
                }
            )
            # response = merge_cart_cookie_to_redis(request, response, user)

            return response


def ImageVerify(request, image_code_id):
    """
    获取图片验证码
    :return:
    """

    name, text, image = captcha.generate_captcha()
    try:
        # 保存当前生成的图片验证码内容
        conn = get_redis_connection('img_code')

        conn.setex('ImageCode_' + image_code_id, 300, text)
    except Exception as e:
        return HttpResponse({'message': 'DBERROR'}, content_type='application/json', status=400)

    return HttpResponse(image, content_type="image/png")






