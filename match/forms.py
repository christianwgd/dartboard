from django.forms import models, ValidationError
from django.utils.translation import gettext as _

from match.models import Match


class MatchForm(models.ModelForm):

    class Meta:
        model = Match
        fields = ['league', 'best_of', 'typus', 'out', 'player1', 'player2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['player1'].choices = []
        self.fields['player2'].choices = []

    def clean(self):
        cleaned_data = super().clean()
        player1 = cleaned_data.get('player1')
        player2 = cleaned_data.get('player2')
        if player1 == player2:
            raise ValidationError(
                _('Player 1 cannot be the same as player 2')
            )
        return cleaned_data
