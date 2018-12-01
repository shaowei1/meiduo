

import requests
import json

from django.conf import settings


class OAuthSina(object):
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state   # 用于保存登录成功后的跳转页面路径


    def get_sina_url(self):
        # 微博登录url参数组建
        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        # 构建url
        sina_url = 'https://api.weibo.com/oauth2/authorize?client_id=' + settings.SINA_CLIENT_ID + '&redirect_uri=' + settings.SINA_REDIRECT_URI
        return sina_url

    def get_access_token(self, code):  # 获取用户token和uid
        url = "https://api.weibo.com/oauth2/access_token"

        querystring = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.request("POST", url, params=querystring)

        return json.loads(response.text)

    def get_user_info(self, access_token_data):
        url = "https://api.weibo.com/2/users/show.json"

        querystring = {
            "uid": access_token_data['uid'],
            "access_token": access_token_data['access_token']
        }

        response = requests.request("GET", url, params=querystring)

        return json.loads(response.text)

