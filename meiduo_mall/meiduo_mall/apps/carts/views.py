from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
import pickle, base64

# Create your views here.
from carts.serializers import CartsSerialziers, CartsListSerialzier, CartsDeleteSerialziers, CartsSelectedSerialziers
from goods.models import SKU


class CartsView(APIView):
    """
        购物车数据的增删改车
    """

    def perform_authentication(self, request):
        # 再调用post方法之前，先不进行request.user
        pass

    def post(self, request):
        # 1、获取前端数据
        data = request.data
        # 2、验证数据
        ser = CartsSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后的数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']
        # 3、判断用户登录状态
        try:
            user = request.user
        except:
            user = None
        # 4、已登录redis
        if user is not None:
            # 1、建立redis连接
            conn = get_redis_connection('cart')
            # 2、保存hash。sku_id和count
            conn.hincrby('cart_%s' % user.id, sku_id, count)
            # 3、保存选中状态。sets
            if selected:
                conn.sadd('cart_selected_%s' % user.id, sku_id)
            # 4、结果返回
            return Response({'count': count})
        else:

            # 5、未登录。cookie
            response = Response({'count': count})
            # 1、获取cookie ，判断以前是否存储过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            # 2、存储过cookie，解密cookie {10: {count: 2, selected: True}}
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
            # 3、未存储过 cart = {}
            else:
                cart = {}
            # 4、根据sku_id获取字典中所对应value，获取到，则说明以前这个sku_id存储过，对count累加
            sku = cart.get(sku_id)
            if sku:
                count += int(sku['count'])
            # 5、字典中写入新数据
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 6、加密字典数据
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            # 7、写入cookie
            response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24)
            # 8、结果返回
            return response

    def get(self, request):


        # 1、判断用户登录状态
        try:
            user = request.user
        except:
            user = None
        # 2、已登录redis
        if user is not None:
            # 1、建立redis连接
            conn = get_redis_connection('cart')
            # 2、获取hash。sku_id和count
            sku_id_count=conn.hgetall('cart_%s' % user.id) #{ sku_id:count}
            # 3、获取选中状态。sets
            sku_ids=conn.smembers('cart_selected_%s' % user.id) # {sku_id1,sku_id2}
            # 4、数据格式统一，构建字典数据 {10:{count:2,selected:True}}
            cart={}
            for sku_id,count in sku_id_count.items():
                cart[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in sku_ids
                }

        else:

            # 5、未登录。cookie
            # 1、获取cookie ，判断以前是否存储过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            # 2、存储过cookie，解密cookie {10: {count: 2, selected: True}}
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
            # 3、未存储过 cart = {}
            else:
                cart = {}

        # 4、获取字典中的sku_id.Dict.keys()
        sku_id_list=cart.keys()
        # 5、根据sku_id获取商品数据对象
        skus=SKU.objects.filter(id__in=sku_id_list)

        for sku in skus:
            sku.count=cart[sku.id]['count']
            sku.selected=cart[sku.id]['selected']
        # 6、序列化返回商品数据对象
        ser=CartsListSerialzier(skus,many=True)
        return Response(ser.data)

    def put(self, request):
        # 1、获取前端数据
        data = request.data
        # 2、验证数据
        ser = CartsSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后的数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']
        # 3、判断用户登录状态
        try:
            user = request.user
        except:
            user = None
        # 4、已登录redis
        if user is not None:
            # 1、建立redis连接
            conn = get_redis_connection('cart')
            # 2、更新hash。sku_id和count
            conn.hset('cart_%s' % user.id, sku_id, count)
            # 3、更新选中状态。sets
            if selected:
                conn.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                conn.srem('cart_selected_%s' % user.id, sku_id)
            # 4、结果返回
            return Response({'count': count})
        else:

            # 5、未登录。cookie
            response = Response({'count': count})
            # 1、获取cookie ，判断以前是否存储过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            # 2、存储过cookie，解密cookie {10: {count: 2, selected: True}}
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
            # 3、未存储过 cart = {}
            else:
                cart = {}

            # 4、字典中写入新数据
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 5、加密字典数据
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            # 6、写入cookie
            response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24)
            # 7、结果返回
            return response

    def delete(self, request):
        # 1、获取前端数据
        data = request.data
        # 2、验证数据
        ser = CartsDeleteSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后的数据
        sku_id = ser.validated_data['sku_id']
        # 3、判断用户登录状态
        try:
            user = request.user
        except:
            user = None
        # 4、已登录redis
        if user is not None:
            # 1、建立redis连接
            conn = get_redis_connection('cart')
            # 2、删除hash。sku_id和count
            conn.hdel('cart_%s' % user.id, sku_id)
            # 3、删除选中状态。sets
            conn.srem('cart_selected_%s' % user.id, sku_id)
            # 4、结果返回
            return Response({'message': 'ok'})
        else:

            # 5、未登录。cookie
            response = Response({'message': 'ok'})
            # 1、获取cookie ，判断以前是否存储过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            # 2、存储过cookie，解密cookie {10: {count: 2, selected: True}}
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))

                # 3、删除数据
                if sku_id in cart.keys():
                    del cart[sku_id]

                # 4、加密字典数据
                cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
                # 5、写入cookie
                response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24)
            # 6、结果返回
            return response

class CartsSelectionView(APIView):
    """
       全选
    """

    def perform_authentication(self, request):
        # 再调用put方法之前，先不进行request.user
        pass

    def put(self, request):
        # 1、获取前端数据
        data = request.data
        # 2、验证数据
        ser = CartsSelectedSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后的数据
        selected = ser.validated_data['selected']
        # 3、判断用户登录状态
        try:
            user = request.user
        except:
            user = None
        # 4、已登录redis
        if user is not None:
            # 1、建立redis连接
            conn = get_redis_connection('cart')
            # 2、获取所有sku_id hash。sku_id和count
            sku_id_count=conn.hgetall('cart_%s' % user.id)
            sku_ids=sku_id_count.keys()
            # 3、更新选中状态。sets
            if selected:
                conn.sadd('cart_selected_%s' % user.id, *sku_ids)
            else:
                conn.srem('cart_selected_%s' % user.id, *sku_ids)
            # 4、结果返回
            return Response({'selected': selected})
        else:

            # 5、未登录。cookie
            response = Response({'selected': selected})
            # 1、获取cookie ，判断以前是否存储过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            # 2、存储过cookie，解密cookie {10: {count: 2, selected: True}}
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))

                # 4、字典中写入新数据
                for sku_id,data in cart.items():
                    data['selected']=selected
                # 5、加密字典数据
                cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
                # 6、写入cookie
                response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24)
            # 7、结果返回
            return response
