# -*- coding:utf-8 -*-
from __future__ import print_function
from django.dispatch import receiver
from . import signals, models
import logging

log = logging.getLogger('django')


@receiver(signals.to_save_linktree, sender=None)
def save_link_tree(sender, **kwargs):
    user = kwargs['user']
    platform = kwargs['platform']
    url = kwargs['url']
    platform, created = models.Platform.objects.get_or_create(
        name=platform
    )
    d = dict((k, kwargs[k]) for k in kwargs if k in ['avatar', 'name'])
    account, created = models.Account.objects.get_or_create(
        user=user,
        defaults=d
    )
    link, created = models.Link.objects.get_or_create(
        account=account,
        platform=platform,
        defaults=dict(
            url=url,
            avatar=d.get('avatar')
        )
    )
    return link
