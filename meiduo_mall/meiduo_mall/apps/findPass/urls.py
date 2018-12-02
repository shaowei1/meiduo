from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<codeid>[\d\w-]+)/$', views.ImageVerify, name="image"),
    url(r'^accounts/(?P<username>[\d\w]+)/sms/token/$', views.NumberToken),
    url(r'^sms_codes/$', views.SmsCode.as_view()),
    url(r'^accounts/(?P<username>[\d\w]+)/password/token/$', views.verifyId.as_view()),
    url(r'^users/(?P<user_id>[\d]+)/password/$', views.RepairPass.as_view())
]

s = 'access_token=eyJhbGciOiJIUzI1NiIsImlhdCI6MTU0MzcxODM4NiwiZXhwIjoxNTQzNzE4Njg2fQ.eyJtb2JpbGUiOiIxODMxMTExMTExMSJ9.e6pU6Vknqt77dzEC-h5u8FlofUnt2bi0Xz4SPC620f0'

# ?text = afzl
# &
# image_code_id = d67c4012 - 2
# a5e - 43
# d2 - 8
# ce0 - 1
# acc96e2a215
