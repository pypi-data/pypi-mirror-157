# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class PlatformSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Platform
        exclude = ()

class AccountSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Account
        exclude = ()


class LinkSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    account_name = serializers.CharField(label='帐号', source='account', read_only=True)
    platform_name = serializers.CharField(label='平台', source='platform', read_only=True)
    class Meta:
        model = models.Link
        exclude = ()
