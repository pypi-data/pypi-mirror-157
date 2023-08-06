from django.contrib import admin

from . import models


@admin.register(models.Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'logo', 'is_active', 'create_time')
    search_fields = ("name",)
    date_hierarchy = 'create_time'


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'avatar', 'is_active', 'create_time')
    search_fields = ('name',)
    date_hierarchy = 'create_time'
    raw_id_fields = ('user',)


@admin.register(models.Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('account', 'platform', 'url', 'avatar', 'is_active', 'create_time')
    date_hierarchy = 'create_time'
    raw_id_fields = ('account', 'platform')
