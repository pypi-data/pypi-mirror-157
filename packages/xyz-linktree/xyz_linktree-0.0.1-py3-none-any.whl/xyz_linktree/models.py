# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models

class Platform(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "平台"
        ordering = ('-create_time',)

    name = models.CharField("名称", max_length=64, unique=True)
    url = models.URLField("URL地址", max_length=256, blank=True, default='')
    logo = models.CharField("logo", max_length=256, blank=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    is_active = models.BooleanField("有效", blank=False, default=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "帐号"
        ordering = ('-create_time',)

    user = models.OneToOneField("auth.user", verbose_name='网站用户', related_name='linktree_account', on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=64, blank=True, default='NO NAME')
    avatar = models.URLField("头像", max_length=256, blank=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    is_active = models.BooleanField("有效", blank=False, default=True)

    def __str__(self):
        return self.name

class Link(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "社链"
        ordering = ('-create_time',)
        unique_together = ('account', 'platform')

    account = models.ForeignKey(Account, verbose_name=Account._meta.verbose_name, related_name='links', on_delete=models.PROTECT)
    platform = models.ForeignKey(Platform, verbose_name=Platform._meta.verbose_name, related_name='links', on_delete=models.PROTECT)
    url = models.URLField("URL地址", max_length=256, blank=True, default='')
    avatar = models.URLField("头像", max_length=256, blank=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    is_active = models.BooleanField("有效", blank=False, default=True)

    def __str__(self):
        return '%s@%s' % (self.account, self.platform)
