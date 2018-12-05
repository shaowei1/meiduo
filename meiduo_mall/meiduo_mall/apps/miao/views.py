# from django.shortcuts import render
#
# # Create your views here.
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
#
# class ZhanshiOrder(APIView):
#
#     def get(self,request):
#
#         # 1、获取前端数据
#         token = request.query_params.get('token', None)
#         if token is None:
#             return Response({'errors': '缺少token'}, status=400)
#         # 2、验证数据。 解密token。{‘name’:python}
#         tjs = TJS(settings.SECRET_KEY, 300
#         try:
#             data = tjs.loads(token)
#         except:
#             return Response({'errors': '无效token'}, status=400)