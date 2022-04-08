# -*- coding: utf-8 -*-
from django.contrib import admin

from match.models import Match, Turn, Leg


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'typus', 'player1', 'player2']
    date_hierarchy = 'timestamp'


@admin.register(Leg)
class LegAdmin(admin.ModelAdmin):
    list_display = ['match', 'ord']
    list_filter = ['match']


@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ['leg', 'player', ]
    list_filter = ['leg', 'player']
