# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import logging

import requests
from django.db.models import Q
from requests import exceptions as req_exceptions

from .django_conf import (
    BKAUTH_TOKEN_APP_CODE,
    BKAUTH_TOKEN_SECRET_KEY,
    ENV_NAME,
    OAUTH_COOKIES_PARAMS,
    OAUTH_PARAMS,
    OAUTH_API_URL,
    IS_BKOAUTH_IN_INSTALLED_APPS,
    OAUTH_NEED_NEW_TOKEN,
    BACKEND_TYPE,
)
from .models import AccessToken
from .utils import transform_uin, get_client_ip

from .exceptions import TokenNotExist, TokenAPIError

LOG = logging.getLogger('component')

# 使用连接池
rpool = requests.Session()


class BaseOAuthClient(object):
    def __init__(self, api_url, auth_cookies_params, **auth_params):
        self.app_code = BKAUTH_TOKEN_APP_CODE
        self.secret_key = BKAUTH_TOKEN_SECRET_KEY
        self.env_name = ENV_NAME
        self.need_new_token = OAUTH_NEED_NEW_TOKEN

        self.api_url = api_url
        self.auth_cookies_params = auth_cookies_params
        self.auth_params = auth_params

        if not self.is_enabled:
            LOG.warning(u'应用的 bkoauth 配置不完整，请检查配置')

    @property
    def is_enabled(self):
        return IS_BKOAUTH_IN_INSTALLED_APPS and self.api_url and self.auth_cookies_params

    def _get_auth_params(self, request):
        """获取用户认证参数
        """
        params = self.auth_params
        for k, v in self.auth_cookies_params.items():
            # 非UIN也会每次检查
            v = transform_uin(request.COOKIES.get(v) or request.session.get(v) or request.GET.get(v, ''))
            params[k] = v
        return params

    def get_app_access_token(self):
        """获取APP基本access_token
        """
        access_token = AccessToken.objects.filter(env_name=ENV_NAME)
        access_token = access_token.filter(Q(user_id__isnull=True) | Q(user_id__exact=''))
        if not access_token:
            data = self._get_app_access_token_data()
            token = AccessToken(
                access_token=data['access_token'],
                refresh_token=data.get('refresh_token', ''),
                scope=data.get('scope', ''),
                env_name=ENV_NAME,
            )
            token.set_expires(data['expires_in'])
            token.save()
            return token
        token = access_token[0]
        # 自动续期
        if token.expires_soon:
            data = self._get_app_access_token_data()
            token.access_token = data['access_token']
            token.refresh_token = data.get('refresh_token', '')
            token.scope = data.get('scope', '')
            token.set_expires(data['expires_in'])
            token.save()
        return token

    def get_access_token(self, request):
        """获取用户access_token
        params: request django request对象
        """
        access_token = AccessToken.objects.filter(env_name=ENV_NAME, user_id=request.user.username)
        if not access_token:
            data = self._get_access_token_data(request)
            token = AccessToken(
                user_id=request.user.username,
                access_token=data['access_token'],
                refresh_token=data.get('refresh_token', ''),
                scope=data.get('scope', ''),
                env_name=ENV_NAME
            )
            token.set_expires(data['expires_in'])
            token.save()
            return token
        token = access_token[0]
        # 自动续期
        if token.expires_soon:
            data = self._get_access_token_data(request)
            token.access_token = data['access_token']
            token.refresh_token = data.get('refresh_token', '')
            token.scope = data.get('scope', '')
            token.set_expires(data['expires_in'])
            token.save()
        return token

    def get_access_token_by_user(self, user_id):
        """通过用户ID获取access_token，适合后台任务场景
        """
        access_token = AccessToken.objects.filter(env_name=ENV_NAME, user_id=user_id)
        if not access_token:
            raise TokenNotExist(u"获取用户【%s】access_token失败，数据库中不存在记录" % user_id)
        token = access_token[0]
        # 自动续期
        if token.expires_soon:
            token = self.refresh_token(token)
        return token

    def refresh_token(self, token):
        """刷新access_token
        params: token AccessToken对象
        """
        if not token.refresh_token:
            raise TokenNotExist(u"【%s】没有refresh_token，不能刷新" % token)
        data = self._get_refresh_token_data(token.refresh_token, token.env_name)
        token.access_token = data['access_token']
        token.refresh_token = data.get('refresh_token', '')
        token.scope = data.get('scope', '')
        token.set_expires(data['expires_in'])
        token.save()
        return token

    def _get_app_access_token_data(self):
        """通过 auth api 获取应用级别的 access_token 数据
        """
        raise NotImplementedError

    def _get_access_token_data(self):
        """通过 auth api 获取用户级别的 access_token 数据
        """
        raise NotImplementedError

    def _get_refresh_token_data(self):
        """通过 auth api 刷新 access_token 数据
        """
        raise NotImplementedError


class OAuthClient(BaseOAuthClient):

    def _is_response_ok(self, resp):
        return resp.get('result')

    def _get_app_access_token_data(self):
        path = '/auth_api/token/'
        url = '%s%s' % (self.api_url, path)
        params = {'app_code': self.app_code,
                  'app_secret': self.secret_key,
                  'env_name': self.env_name,
                  'grant_type': 'client_credentials',
                  'need_new_token': self.need_new_token,
                  }
        try:
            resp = rpool.get(url, params=params, timeout=10, verify=False)
            resp = resp.json()
        except req_exceptions.MissingSchema:
            raise TokenAPIError(
                u"Django配置项【OAUTH_API_URL】未找到，请检查配置")
        except Exception as error:
            LOG.exception(u"获取APP级别access_token异常: %s" % error)
            raise TokenAPIError(error.message)

        if not self._is_response_ok(resp):
            LOG.error(u"获取APP级别access_token错误: %s" % resp.get('message', ''))
            raise TokenAPIError(resp.get('message', ''))

        return resp['data']

    def _get_access_token_data(self, request):
        path = '/auth_api/token/'
        url = '%s%s' % (self.api_url, path)
        params = {'app_code': self.app_code,
                  'app_secret': self.secret_key,
                  'env_name': self.env_name,
                  'bk_client_ip': get_client_ip(request),
                  'grant_type': 'authorization_code',
                  'need_new_token': self.need_new_token,
                  }
        params.update(self._get_auth_params(request))
        try:
            resp = rpool.get(url, params=params, timeout=10, verify=False)
            resp = resp.json()
        except req_exceptions.MissingSchema:
            raise TokenAPIError(
                u"Django配置项【OAUTH_API_URL】未找到，请检查配置")
        except Exception as error:
            LOG.exception(u"获取用户级别access_token异常: %s" % error)
            raise TokenAPIError(error.message)

        if not self._is_response_ok(resp):
            LOG.error(u'获取用户级别access_token错误: %s' % resp.get('message', ''))
            raise TokenAPIError(resp.get('message', ''))

        return resp['data']

    def _get_refresh_token_data(self, refresh_token, env_name):
        path = '/auth_api/refresh_token/'
        url = '%s%s' % (self.api_url, path)
        params = {'grant_type': 'refresh_token',
                  'app_code': self.app_code,
                  'env_name': env_name,
                  'refresh_token': refresh_token,
                  'need_new_token': self.need_new_token,
                  }
        try:
            resp = rpool.get(url, params=params, timeout=10, verify=False)
            resp = resp.json()
        except req_exceptions.MissingSchema:
            raise TokenAPIError(
                u"Django配置项【OAUTH_API_URL】未找到，请检查配置")
        except Exception as error:
            LOG.exception(u"刷新access_token异常: %s" % error)
            raise TokenAPIError(error.message)

        if not self._is_response_ok(resp):
            LOG.error(u'刷新access_token错误: %s' % resp.get('message', ''))
            raise TokenAPIError(resp.get('message', ''))

        return resp['data']


class OAuthClientEE(BaseOAuthClient):
    def _is_response_ok(self, resp):
        return resp.get('code') == 0

    def _get_headers(self):
        return {"X-BK-APP-CODE": self.app_code, "X-BK-APP-SECRET": self.secret_key}

    def _get_app_access_token_data(self):
        path = '/api/v1/auth/access-tokens'
        url = '%s%s' % (self.api_url, path)
        params = {
            'grant_type': 'client_credentials',
            'id_provider': 'client',
        }
        try:
            resp = rpool.post(url, json=params, headers=self._get_headers(), timeout=10, verify=False)
            resp = resp.json()
        except req_exceptions.MissingSchema:
            raise TokenAPIError(
                u"Django配置项【OAUTH_API_URL】未找到，请检查配置")
        except Exception as error:
            LOG.exception(u"获取APP级别access_token异常: %s" % error)
            raise TokenAPIError(error.message)

        if not self._is_response_ok(resp):
            LOG.error(u"获取APP级别access_token错误: %s" % resp.get('message', ''))
            raise TokenAPIError(resp.get('message', ''))

        return resp['data']

    def _get_access_token_data(self, request):
        path = '/api/v1/auth/access-tokens'
        url = '%s%s' % (self.api_url, path)
        params = {
            'grant_type': 'authorization_code',
            'id_provider': 'bk_login',
        }
        params.update(self._get_auth_params(request))
        try:
            resp = rpool.post(url, json=params, headers=self._get_headers(), timeout=10, verify=False)
            resp = resp.json()
        except req_exceptions.MissingSchema:
            raise TokenAPIError(
                u"Django配置项【OAUTH_API_URL】未找到，请检查配置")
        except Exception as error:
            LOG.exception(u"获取用户级别access_token异常: %s" % error)
            raise TokenAPIError(error.message)

        if not self._is_response_ok(resp):
            LOG.error(u'获取用户级别access_token错误: %s' % resp.get('message', ''))
            raise TokenAPIError(resp.get('message', ''))

        return resp['data']

    def _get_refresh_token_data(self, refresh_token, env_name):
        path = '/api/v1/auth/access-tokens/refresh'
        url = '%s%s' % (self.api_url, path)
        params = {'refresh_token': refresh_token}
        try:
            resp = rpool.post(url, json=params, headers=self._get_headers(), timeout=10, verify=False)
            resp = resp.json()
        except req_exceptions.MissingSchema:
            raise TokenAPIError(
                u"Django配置项【OAUTH_API_URL】未找到，请检查配置")
        except Exception as error:
            LOG.exception(u"刷新access_token异常: %s" % error)
            raise TokenAPIError(error.message)

        if not self._is_response_ok(resp):
            LOG.error(u'刷新access_token错误: %s' % resp.get('message', ''))
            raise TokenAPIError(resp.get('message', ''))

        return resp['data']


if BACKEND_TYPE == 'bk_token':
    oauth_client = OAuthClientEE(OAUTH_API_URL, OAUTH_COOKIES_PARAMS, **OAUTH_PARAMS)
else:
    oauth_client = OAuthClient(OAUTH_API_URL, OAUTH_COOKIES_PARAMS, **OAUTH_PARAMS)
