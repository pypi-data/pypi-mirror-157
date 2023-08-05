# -*- coding:utf-8 -*-
from __future__ import division

from xyz_restful.mixins import BatchActionMixin
from . import models, serializers
from rest_framework import viewsets, decorators, response
from xyz_restful.decorators import register

@register()
class PlatformViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Platform.objects.all()
    serializer_class = serializers.PlatformSerializer
    search_fields = ('name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'name', 'create_time')


@register()
class AccountViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    search_fields = ('name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'name', 'create_time')


@register()
class LinkViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Link.objects.all()
    serializer_class = serializers.LinkSerializer
    search_fields = ('name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'account': ['in', 'exact'],
        'platform': ['in', 'exact'],
        'is_active': ['exact'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'name', 'create_time')


