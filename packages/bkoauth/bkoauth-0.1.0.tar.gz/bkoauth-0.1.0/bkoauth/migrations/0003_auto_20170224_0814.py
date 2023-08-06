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

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bkoauth', '0002_auto_20161117_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesstoken',
            name='env_name',
            field=models.CharField(max_length=255, verbose_name='\u90e8\u7f72\u73af\u5883', db_index=True),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='user_id',
            field=models.CharField(db_index=True, max_length=64, null=True, verbose_name=b'user_id', blank=True),
        ),
    ]
