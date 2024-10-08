from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.contrib import auth
from django.utils.translation import gettext as _

from player.models import Player, League

User = auth.get_user_model()


class PlayerForm(forms.models.ModelForm):

    username = forms.CharField(
        label=_('username'), required=False, max_length=150
    )
    email = forms.EmailField(
        label=_('Email'), required=False,
        help_text=_(
            'Dartboard supports Gravatar, if you register your email '
            'at <a href="https://de.gravatar.com/" target="_blank">gravatar.com</a>'
        )
    )
    first_name = forms.CharField(
        label=_('first name'), required=False, max_length=150
    )
    last_name = forms.CharField(
        label=_('last name'), required=False, max_length=150
    )

    class Meta:
        model = Player
        fields = ['username', 'first_name', 'last_name', 'nickname', 'email']


class UserForm(forms.models.ModelForm):

    nickname = forms.CharField(
        label=_('Nickname'), max_length=50, required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'nickname', 'email']


class LeagueForm(BSModalModelForm):

    class Meta:
        model = League
        fields = ['name']


class PlayerSelectForm(BSModalModelForm):

    class Meta:
        model = League
        fields = ['players']
