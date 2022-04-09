from django.forms import models

from match.models import Match


class MatchForm(models.ModelForm):

    class Meta:
        model = Match
        fields = ['league', 'typus', 'best_of', 'player1', 'player2']
