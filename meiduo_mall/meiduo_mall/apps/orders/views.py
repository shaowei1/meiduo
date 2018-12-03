from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from django_redis import get_redis_connection
from decimal import Decimal

# Create your views here.
from goods.models import SKU
from goods.utils import PageNum
from orders.models import OrderGoods, OrderInfo
from orders.serializers import OrderShowSerializers, OrderSaveSerializers, OrderSerializer, OrderGoodSerializer
from users.models import User


class OrdersShowView(APIView):
    """
        展示订单信息
    """

    def get(self, request):
        # 1、获取用户对象
        user = request.user
        # 2、建立redis连接
        conn = get_redis_connection('cart')
        # 3、获取hash数据sku_id count
        sku_id_count = conn.hgetall('cart_%s' % user.id)  # {10:1}
        cart = {}
        for sku_id, count in sku_id_count.items():
            cart[int(sku_id)] = int(count)
        # 4、获取集合数据
        sku_ids = conn.smembers('cart_selected_%s' % user.id)
        # 5、查询选中状态的数据对象
        skus = SKU.objects.filter(id__in=sku_ids)
        # 6、商品对象添加count数量
        for sku in skus:
            sku.count = cart[sku.id]
        # 7、生成运费
        freight = Decimal(10.00)
        # 8、序列化返回商品对象
        ser = OrderShowSerializers({'freight': freight, 'skus': skus})

        return Response(ser.data)


class OrderSaveView(CreateAPIView, ListAPIView):
    """
        保存订单信息
    """
    serializer_class = OrderSaveSerializers


class GoPay(APIView):
    pass


class AllOrdersView(ListAPIView):
    pagination_class = PageNum
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # user_id = User.objects.get(username=user)
        return OrderInfo.objects.filter(user_id=user.id)


class GoodComment(ListAPIView):
    serializer_class = OrderGoodSerializer

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderGoods.objects.filter(order_id=order_id).order_by('create_time')



