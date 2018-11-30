from django.conf.urls import url
from django.contrib import admin
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SmsCodeView.as_view()),
    url(r'^usernames/(?P<username>\w+)/count/$', views.UserNameView.as_view()),
    url(r'^mobiles/(?P<mobile>\d+)/count/$', views.MobileView.as_view()),
    url(r'^users/$', views.UsersView.as_view()),
    # url(r'^authorizations/$', obtain_jwt_token),
    url(r'^authorizations/$', views.UserLoginView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'email/$', views.EmailView.as_view()),
    url(r'emails/verification/$', views.EmailVerifyView.as_view()),
    url(r'browse_histories/$', views.SKUHistoriesView.as_view()),

]
