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
import datetime

from django.db import models
try:
    from django.utils import timezone
    has_timezone = True
except ImportError:
    has_timezone = False

from .django_conf import EXPIRES_SECONDS, BKAUTH_TOKEN_APP_CODE


class AccessToken(models.Model):
    access_token = models.CharField(u"Access Token", max_length=255, unique=True)
    expires = models.DateTimeField(u"Access Token过期时间")
    refresh_token = models.CharField(u"Refresh Token", max_length=255, null=True, blank=True)
    scope = models.TextField(u"权限范围", null=True, blank=True)
    env_name = models.CharField(u"部署环境", max_length=255, db_index=True)
    user_id = models.CharField('user_id', max_length=64, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(u"创建时间", auto_now_add=True)
    extra = models.TextField(u"其他", null=True, blank=True)

    class Meta:
        app_label = 'bkoauth'
        db_table = 'bkoauth_access_token'
        verbose_name = 'AccessToken'
        verbose_name_plural = 'AccessToken'

    def __unicode__(self):
        if self.user_id:
            return '<user(%s), access_token(%s)>' % (self.user_id, self.access_token)
        else:
            # APP级别access_token
            return '<app(%s), access_token(%s)>' % (BKAUTH_TOKEN_APP_CODE, self.access_token)

    @property
    def expires_soon(self):
        """判断是否即将过期
        """
        return self.expires - self.now() < datetime.timedelta(seconds=EXPIRES_SECONDS)

    def set_expires(self, expires_in):
        self.expires = self.now() + datetime.timedelta(seconds=expires_in)

    def now(self):
        if has_timezone:
            return timezone.now()
        else:
            return datetime.datetime.now()
