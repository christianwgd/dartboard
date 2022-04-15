from django.forms import models

from match.models import Match


class MatchForm(models.ModelForm):

    class Meta:
        model = Match
        fields = ['league', 'best_of', 'typus', 'out', 'player1', 'player2']
