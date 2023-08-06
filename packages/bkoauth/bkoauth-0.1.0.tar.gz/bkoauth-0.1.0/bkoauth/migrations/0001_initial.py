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
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(unique=True, max_length=255, verbose_name='Access Token')),
                ('expires', models.DateTimeField(verbose_name='Access Token\u8fc7\u671f\u65f6\u95f4')),
                ('refresh_token', models.CharField(unique=True, max_length=255, verbose_name='Refresh Token')),
                ('scope', models.TextField()),
                ('env_name', models.CharField(max_length=255, verbose_name='\u90e8\u7f72\u73af\u5883')),
                ('user_id', models.CharField(max_length=64, null=True, verbose_name=b'user_id', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('extra', models.TextField(null=True, verbose_name='\u5176\u4ed6', blank=True)),
            ],
            options={
                'db_table': 'bkoauth_access_token',
                'verbose_name': 'AccessToken',
                'verbose_name_plural': 'AccessToken',
            },
        ),
    ]
