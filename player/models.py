from django.db import models
from django.contrib import auth
from django.utils.translation import gettext as _


User = auth.get_user_model()


class Player(models.Model):
    class Meta:
        verbose_name = _("Player")
        verbose_name_plural = _("Players")
        ordering = ['user__username']

    def __str__(self):
        return self.nickname or self.user.username

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        verbose_name=_("User"), related_name='player'
    )
    nickname = models.CharField(
        _('Nickname'), max_length=50, null=True, blank=True
    )


class League(models.Model):
    class Meta:
        verbose_name = _("League")
        verbose_name_plural = _("Leagues")
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_manager(self, player):
        return player in self.managers

    name = models.CharField(_('Name'), max_length=50)
    players = models.ManyToManyField(
        Player, verbose_name=_('Players'),
        blank=True, related_name='leagues'
    )
    managers = models.ManyToManyField(
        Player, verbose_name=_('Manager'),
        related_name='managed_leagues'
    )
