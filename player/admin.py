# -*- coding: utf-8 -*-
from avatar.templatetags.avatar_tags import avatar
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from player.models import Player, League


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'player_name', ]
    list_display_links = ['image_tag', 'player_name']

    @staticmethod
    def player_name(obj):
        return obj.nickname or obj.user.username

    player_name.short_description = _('Player name')
    player_name.allow_tags = True

    @staticmethod
    def image_tag(obj):
        return avatar(obj.ref_usr, 20)

    image_tag.short_description = _('Image')
    image_tag.allow_tags = True


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name']
