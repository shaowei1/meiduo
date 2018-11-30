import pickle

import base64
import re
from django.contrib.auth.backends import ModelBackend
from django_redis import get_redis_connection

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
    }


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 1、判断username是否是手机号
            if re.match(r'^1[3-9]\d{9}$', username):
                # 2、是手机号，按照手机号查询数据 mobile
                user = User.objects.get(mobile=username)
            else:
                # 3、不是则按照username字段查询
                user = User.objects.get(username=username)
        except:
            user = None

        # 4、验证密码
        if user is not None and user.check_password(password):
            return user


def merge_cart_cookie_to_redis(request,response,user):
    # 1、获取cookie
    cart_cookie = request.COOKIES.get('cart_cookie', None)
    # 2、判断cookie是否存在
    if cart_cookie is None:
        return response
    # 3、解密cookie {10: {count: 2, selected: True}} {}
    cart = pickle.loads(base64.b64decode(cart_cookie))
    # 4、判断字典是否为空
    if not cart:
        return response
    # 5、拆分数据 字典对应hash类 列表对应set
    cart_dict = {}
    sku_ids = []
    sku_ids_none = []
    for sku_id, data in cart.items():
        # 哈希
        cart_dict[sku_id] = data['count']
        # 选中状态
        if data['selected']:
            sku_ids.append(sku_id)
        else:
            sku_ids_none.append(sku_id)

    # 6、建立连接写入redis缓存
    conn = get_redis_connection('cart')
    conn.hmset('cart_%s' % user.id, cart_dict)
    if sku_ids:
        conn.sadd('cart_selected_%s' % user.id, *sku_ids)
    if sku_ids_none:
        conn.srem('cart_selected_%s' % user.id, *sku_ids_none)
    # 7、删除cookie
    response.delete_cookie('cart_cookie')
    # 8、结果返回
    return response
