from django.contrib import admin
from .models import Player, RoundScore


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_score')
    search_fields = ('name',)


@admin.register(RoundScore)
class RoundScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'score', 'date_played')
    list_filter = ('date_played',)
    search_fields = ('player__name',)

# Register your models here.
