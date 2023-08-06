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
import os
import json

from django.conf import settings


# 默认过期时间, 24小时
DEFAULT_EXPIRES_SECONDS = 60 * 60 * 24

APP_CODE = getattr(settings, 'APP_CODE', None)
SECRET_KEY = getattr(settings, 'SECRET_KEY', None)
# Auth API request credentials, if not provided, will use APP_CODE/SECRET_KEY as a fallback option
BKAUTH_TOKEN_APP_CODE = getattr(settings, 'BKAUTH_TOKEN_APP_CODE', None) or APP_CODE
BKAUTH_TOKEN_SECRET_KEY = getattr(settings, 'BKAUTH_TOKEN_SECRET_KEY', None) or SECRET_KEY

RUN_MODE = getattr(settings, 'RUN_MODE', 'DEVELOP')
APIGW_PUBLIC_KEY = getattr(settings, 'APIGW_PUBLIC_KEY', '')
# 过期时间
EXPIRES_SECONDS = getattr(settings, 'EXPIRES_SECONDS', DEFAULT_EXPIRES_SECONDS)

# env
ENV_NAME = 'prod' if RUN_MODE == 'PRODUCT' else 'test'

# OAuth API地址
# 从环境变量中获取
oauth_api_url_env = os.environ.get('OAUTH_API_URL', '')
# 从Django配置项中获取
oauth_api_url_dj = getattr(settings, 'OAUTH_API_URL', '')
OAUTH_API_URL = oauth_api_url_env or oauth_api_url_dj

# OAuth从cookies获得参数
# 从环境变量中获取
try:
    oauth_cookies_params_env = json.loads(os.environ.get('OAUTH_COOKIES_PARAMS', '{}'))
except Exception:
    oauth_cookies_params_env = {}

# 从Django配置项中获取
oauth_cookies_params_dj = getattr(settings, 'OAUTH_COOKIES_PARAMS', {})
OAUTH_COOKIES_PARAMS = oauth_cookies_params_env or oauth_cookies_params_dj

# OAuth其他参数
# 从环境变量中获取
try:
    oauth_params_env = json.loads(os.environ.get('OAUTH_PARAMS', '{}'))
except Exception:
    oauth_params_env = {}
# 从Django配置项中获取
oauth_params_dj = getattr(settings, 'OAUTH_PARAMS', {})
OAUTH_PARAMS = oauth_params_env or oauth_params_dj

IS_BKOAUTH_IN_INSTALLED_APPS = 'bkoauth' in settings.INSTALLED_APPS

# OAuth 申请或刷新 token 时，是否需要新的 token
OAUTH_NEED_NEW_TOKEN = getattr(settings, 'OAUTH_NEED_NEW_TOKEN', True)

# OAuth BACKEND Type
# 从环境变量中获取
oauth_backend_type_env = os.environ.get('BKAUTH_BACKEND_TYPE', '')
# 从Django配置项中获取
oauth_backend_type_dj = getattr(settings, 'BKAUTH_BACKEND_TYPE', '')
BACKEND_TYPE = oauth_backend_type_env or oauth_backend_type_dj
