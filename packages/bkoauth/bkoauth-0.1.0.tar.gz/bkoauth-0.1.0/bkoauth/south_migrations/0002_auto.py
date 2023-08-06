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
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'AccessToken', fields ['user_id']
        db.create_index('bkoauth_access_token', ['user_id'])

        # Adding index on 'AccessToken', fields ['env_name']
        db.create_index('bkoauth_access_token', ['env_name'])


    def backwards(self, orm):
        # Removing index on 'AccessToken', fields ['env_name']
        db.delete_index('bkoauth_access_token', ['env_name'])

        # Removing index on 'AccessToken', fields ['user_id']
        db.delete_index('bkoauth_access_token', ['user_id'])


    models = {
        'bkoauth.accesstoken': {
            'Meta': {'object_name': 'AccessToken', 'db_table': "'bkoauth_access_token'"},
            'access_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'env_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'scope': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['bkoauth']