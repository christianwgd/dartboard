from django.db import models
from django.utils.translation import gettext as _

from player.models import Player, League


MATCH_TYPE_CHOICES = (
    ('301', _('301')),
    ('501', _('501')),
    ('701', _('701')),
)


class Match(models.Model):
    """
    A darts match
    """
    class Meta:
        verbose_name = _("Match")
        verbose_name_plural = _("Matches")
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.timestamp} {self.typus}: {self.player1} - {self.player2}'

    typus = models.CharField(
        verbose_name=_('Type'), max_length=3,
        choices=MATCH_TYPE_CHOICES, default='501'
    )
    best_of = models.PositiveSmallIntegerField(
        default=3, verbose_name=_('best of')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Date of match')
    )
    player1 = models.ForeignKey(
        Player, verbose_name=_('Player 1'),
        on_delete=models.SET_NULL, null=True,
        related_name='player1'

    )
    player2 = models.ForeignKey(
        Player, verbose_name=_('Player 2'),
        on_delete=models.SET_NULL, null=True,
        related_name='player2'
    )
    league = models.ForeignKey(
        League, verbose_name=_('League'),
        on_delete=models.CASCADE
    )
    winner = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        related_name='match_wins', verbose_name=_('Winner'),
        null=True, blank=True
    )


class Leg(models.Model):
    """
    One game in a match is called 'leg'
    """
    class Meta:
        verbose_name = _("Leg")
        verbose_name_plural = _("Legs")

    def __str__(self):
        return f'{self.match} Leg {self.ord}'

    match = models.ForeignKey(
        Match, on_delete=models.CASCADE,
        related_name='legs', verbose_name=_('match')
    )
    ord = models.PositiveSmallIntegerField(default=1, verbose_name=_('Ordinal'))
    winner = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        related_name='leg_wins', verbose_name=_('Winner'),
        null=True, blank=True
    )


class Turn(models.Model):
    """
    A three dart turn in a leg
    """
    class Meta:
        verbose_name = _('Turn')
        verbose_name_plural = _('Turns')

    def __str__(self):
        return f'{self.leg} {self.player}'

    leg = models.ForeignKey(
        Leg, on_delete=models.CASCADE,
        verbose_name=_('Leg'), related_name='rounds'
    )
    player = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True,
        verbose_name=_('Player'), related_name='turns'
    )
    throw1 = models.PositiveSmallIntegerField(default=0, verbose_name=_('Throw 1'))
    throw2 = models.PositiveSmallIntegerField(default=0, verbose_name=_('Throw 2'))
    throw3 = models.PositiveSmallIntegerField(default=0, verbose_name=_('Throw 3'))