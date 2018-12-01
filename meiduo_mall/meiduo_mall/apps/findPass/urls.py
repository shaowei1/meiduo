from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<codeid>[\d\w-]+)/$', views.ImageVerify, name="image")
]
