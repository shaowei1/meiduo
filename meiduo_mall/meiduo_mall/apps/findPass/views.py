from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.utils import constants
from meiduo_mall.utils.captcha.captcha import captcha


def ImageVerify(request, codeid):
    """
    获取图片验证码
    :return:
    """

    name, text, image = captcha.generate_captcha()
    try:
        # 保存当前生成的图片验证码内容
        conn = get_redis_connection('history')

        conn.setex('ImageCode_' + codeid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        return HttpResponse('error')

    return HttpResponse(image, content_type="image/png")
