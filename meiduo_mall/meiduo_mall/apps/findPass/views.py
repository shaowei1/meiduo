from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.utils import constants
from meiduo_mall.utils.captcha.captcha import captcha
from meiduo_mall.utils.regular import phone_number


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

    return HttpResponse(image, content_type="image/png")


def NumberToken(request, username):
    """
    获取手机号和token
    :param request:
    :param phone_number:
    :return:
    """
    if phone_number.match(username).group():
        print(phone_number)
        return
        pass

    text = request.GET.get('text')
    image_code_id = request.GET.get('image_code_id')
    print(text)
    print(image_code_id)

    pass
