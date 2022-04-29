# -*- coding: utf-8 -*-
from django.contrib import admin

from match.models import Match, Turn, Leg


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'typus', 'league', 'player1', 'player2', 'winner']
    list_filter = ['typus']
    date_hierarchy = 'timestamp'


@admin.register(Leg)
class LegAdmin(admin.ModelAdmin):
    list_display = ['match', 'ord', 'winner']
    list_filter = ['match']


@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ['leg', 'ord', 'player', ]
    list_filter = ['leg', 'player']
