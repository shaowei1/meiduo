from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView,CreateAPIView,UpdateAPIView,DestroyAPIView
# Create your views here.
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import AreasSerializers, AddressSerializers
from users.models import Address


class AreasView(CacheResponseMixin,ListAPIView):
    """
        获取省的信息
    """
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreasSerializers


class AreaView(CacheResponseMixin,ListAPIView):
    """
        获取市和区县的信息
    """
    # queryset = Area.objects.filter(parent_id=pk)
    serializer_class = AreasSerializers

    # @cache_response(timeout= 60*60 ,cache='default')
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Area.objects.filter(parent_id=pk)

class AddressView(CreateAPIView,UpdateAPIView,DestroyAPIView):
    """
        保存收获地址
    """
    # queryset = Address.objects.filter(user=)
    serializer_class = AddressSerializers


    def get_queryset(self):

         return Address.objects.filter(user=self.request.user,is_deleted=False)

    def get(self,request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({'addresses':serializer.data})


    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # 逻辑删除
        instance.is_deleted=True
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


