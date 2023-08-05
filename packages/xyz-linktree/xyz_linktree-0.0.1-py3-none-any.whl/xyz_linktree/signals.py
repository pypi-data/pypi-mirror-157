# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import Signal

to_save_linktree = Signal(providing_args=["platform", "user", "url", "avatar", "name"])