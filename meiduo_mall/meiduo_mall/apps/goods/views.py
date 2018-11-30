from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from drf_haystack.viewsets import HaystackViewSet
# Create your views here.
from goods.models import GoodsCategory, SKU
from goods.serializers import SKUListSerialziers, SKUSearchSerializers
from goods.utils import PageNum



class CategoriesView(APIView):

    """
        面包屑导航，分类数据获取
    """
    def get(self,request,pk):
        # 1、获取前端数据。正则匹配
        # 2、根据id查询三级分类对象
        cat3=GoodsCategory.objects.get(id=pk)
        # 3、根据三级分类获取一级和二级分类
        cat2=cat3.parent
        cat1=cat2.parent
        # 4、结果返回
        return Response({
            'cat1':cat1.name,
            'cat2':cat2.name,
            'cat3':cat3.name,
        })



class SKUListView(ListAPIView):

    """
        获取当前分类下所有商品数据
    """

    # queryset = SKU.objects.filter(category_id=pk)
    serializer_class = SKUListSerialziers

    pagination_class = PageNum
    filter_backends = [OrderingFilter]
    ordering_fields=('create_time','sales','price')

    def get_queryset(self):
        pk=self.kwargs['pk']
        return SKU.objects.filter(category_id=pk)


class SKUSearchView(HaystackViewSet):

    index_models = [SKU]
    serializer_class = SKUSearchSerializers
    pagination_class = PageNum

