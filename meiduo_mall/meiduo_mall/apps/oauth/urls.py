from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^qq/authorization/$', views.OauthLoginView.as_view()),
    url(r'^sina/authorization/$', views.SinaLoginView.as_view()),
    url(r'^qq/user/$', views.OauthView.as_view()),
    # url(r'^sina/user/$', views.OauthView.as_view()),
]
