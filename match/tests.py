from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _
from faker import Faker

from match.forms import MatchForm
from match.models import Match, Leg, Turn
from player.models import League, Player


User = auth.get_user_model()


class MatchTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.league = League.objects.create(
            name=self.fake.word(),
        )
        for _ in range(3):
            user = User.objects.create(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=self.fake.email()
            )
            player = Player.objects.create(
                user=user
            )
            self.league.players.add(player)
        self.league.managers.add(Player.objects.first())
        self.match = Match.objects.create(
            player1=Player.objects.first(),
            player2=Player.objects.last(),
            league=self.league
        )
        self.leg = Leg.objects.create(
            match=self.match
        )
        self.turn = Turn.objects.create(
            leg=self.leg,
            player=self.match.player1,
        )

    # Model Tests
    def test_match_str(self):
        tmstmp = formats.date_format(
            timezone.localtime(self.match.timestamp),
            'SHORT_DATETIME_FORMAT'
        )
        self.assertEqual(
            self.match.__str__(),
            f'{self.match.typus}: {self.match.player1} - {self.match.player2} ({tmstmp})'
        )

    def test_leg_str(self):
        self.assertEqual(
            self.leg.__str__(),
            f'{self.leg.match} Leg {self.leg.ord}'
        )

    def test_turn_str(self):
        self.assertEqual(
            self.turn.__str__(),
            f'{self.turn.leg} {self.turn.player}'
        )

    # Form Tests
    def test_match_form_valid(self):
        player1 = Player.objects.first()
        player2 = Player.objects.last()
        form_data = {
            'league': self.league,
            'best_of': 3,
            'typus': '501',
            'out': 'DO',
            'player1': player1,
            'player2': player2
        }
        form = MatchForm(form_data)
        self.assertTrue(form.is_valid())

    def test_match_form_invalid_same_players(self):
        player1 = Player.objects.first()
        player2 = player1
        form_data = {
            'league': self.league,
            'best_of': 3,
            'typus': '501',
            'out': 'DO',
            'player1': player1,
            'player2': player2
        }
        form = MatchForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn(
            _('Player 2 cannot be the same as player 1'),
            form.errors['player2']
        )

    def test_match_form_invalid_empty(self):
        form_data = {}
        form = MatchForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)

    # View Tests
    def test_match_create_view_no_auth(self):
        url = reverse('match:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_board_view(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unfinished']), 1)
        player1 = Player.objects.first()
        player2 = Player.objects.last()
        form_data = {
            'league': self.league.id,
            'best_of': 3,
            'typus': '501',
            'out': 'DO',
            'player1': player1.id,
            'player2': player2.id
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        new_match = Match.objects.latest('timestamp')
        self.assertEqual(response.url, reverse('match:board', kwargs={'pk': new_match.id}))
