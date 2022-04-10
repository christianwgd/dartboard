from django import forms
from django.contrib import auth
from django.utils.translation import gettext as _

from player.models import Player


User = auth.get_user_model()


class PlayerForm(forms.models.ModelForm):

    email = forms.EmailField(
        label=_('Email'), required=False,
        help_text=_(
            'Dartboard supports Gravatar, if you register your email '
            'at <a href="https://de.gravatar.com/" target="_blank">gravatar.com</a>'
        )
    )
    first_name = forms.CharField(
        label=_('first name'), required=False,
    )
    last_name = forms.CharField(
        label=_('last name'), required=False,
    )

    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'nickname', 'email']


class UserForm(forms.models.ModelForm):

    nickname = forms.CharField(
        label=_('Nickname'), max_length=50, required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'nickname', 'email']
