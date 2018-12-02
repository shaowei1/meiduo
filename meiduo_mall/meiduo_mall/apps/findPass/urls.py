from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<codeid>[\d\w-]+)/$', views.ImageVerify, name="image"),
    url(r'^accounts/(?P<username>[\d\w]+)/sms/token/$', views.NumberToken)
]

s = 'http://api.meiduo.site:8000/accounts/python/sms/token/?text=afzl&image_code_id=d67c4012-2a5e-43d2-8ce0-1acc96e2a215'

# ?text = afzl
# &
# image_code_id = d67c4012 - 2
# a5e - 43
# d2 - 8
# ce0 - 1
# acc96e2a215
