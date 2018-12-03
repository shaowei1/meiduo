from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<codeid>[\d\w-]+)/$', views.ImageVerify, name="image"),
    url(r'^accounts/(?P<username>[\d\w]+)/sms/token/$', views.NumberToken),
    url(r'^sms_codes/$', views.SmsCode.as_view()),
    url(r'^accounts/(?P<username>[\d\w]+)/password/token/$', views.VerifyId.as_view()),
    url(r'^users/(?P<user_id>[\d]+)/password/$', views.RepairPass.as_view()),
]